from __future__ import annotations

import collections.abc as c
import shutil
import subprocess
import tempfile
import typing as t
from pathlib import Path

from build.__main__ import main as build_main

if t.TYPE_CHECKING:
    import _typeshed as _t

BASE_DIR = Path(__file__).parent


def walk(__dir: Path, /) -> c.Iterable[Path]:
    """Walk through a directory and yield all files."""
    for path in __dir.iterdir():
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from walk(path)


class Setup:
    _7Z_EXE: Path = BASE_DIR / "7zr.exe"
    _7ZSD_SFX: Path = BASE_DIR / "7zSD.sfx"

    def __init__(
        self,
        project_dir: _t.StrPath | None = None,
        build_dir: _t.StrPath | None = None,
        dist_dir: _t.StrPath | None = None,
        setup_bat_template: _t.StrPath | None = None,
        cfg_template: _t.StrPath | None = None,
        files: c.Iterable[tuple[_t.StrPath, _t.StrPath] | _t.StrPath] | None = None,
        sfx_title: str = "Installer",
        bootstrap_args: c.Iterable[str] = (),
        **kwargs: t.Any,
    ) -> None:
        # project_dir
        if project_dir is None:
            self.project_dir = Path.cwd()
        else:
            self.project_dir = Path(project_dir)
            if not self.project_dir.is_absolute():
                self.project_dir = BASE_DIR / project_dir
        # build_dir
        if build_dir is None:
            self.build_dir = BASE_DIR / "build"
        else:
            self.build_dir = Path(build_dir)
            if not self.build_dir.is_absolute():
                self.build_dir = self.project_dir / build_dir
        self.archive_dir = self.build_dir / "archive"
        # dist_dir
        if dist_dir is None:
            self.dist_dir = BASE_DIR / "dist"
        else:
            self.dist_dir = Path(dist_dir)
            if not self.dist_dir.is_absolute():
                self.dist_dir = self.project_dir / dist_dir
        # setup_bat
        if setup_bat_template is None:
            self.setup_bat = BASE_DIR / "setup.python3.12.9.bat.template"
        else:
            self.setup_bat = Path(setup_bat_template)
            if not self.setup_bat.is_absolute():
                self.setup_bat = BASE_DIR / setup_bat_template
        # installer_cfg
        if cfg_template is None:
            self.installer_cfg = BASE_DIR / "installer.cfg.template"
        else:
            self.installer_cfg = Path(cfg_template)
            if not self.installer_cfg.is_absolute():
                self.installer_cfg = BASE_DIR / cfg_template
        # files
        self.files = tuple(files) if files is not None else ()
        # sfx
        self.sfx_title = sfx_title
        # bootstrap_args
        self.bootstrap_args = tuple(bootstrap_args)
        self.kwargs = kwargs

    def build_whl(self) -> Path:
        with tempfile.TemporaryDirectory(dir=self.archive_dir) as outdir:
            outdir_path = Path(outdir)
            build_main(["--wheel", "--outdir", outdir, str(self.project_dir)])
            try:
                file = next(outdir_path.iterdir())
                if not file.suffix == ".whl":
                    raise StopIteration
            except StopIteration:
                raise FileNotFoundError("No .whl file found in the output directory.") from None
            ret_path = shutil.move(file, self.archive_dir)
        self.whl_file = Path(ret_path)
        return self.whl_file

    def create_setup_bat(self) -> Path:
        content = self.setup_bat.read_text("ansi")
        content = content.replace(
            "{bootstrap_args}",
            subprocess.list2cmdline(self.bootstrap_args).format(
                whl_file=self.whl_file.name, **self.kwargs
            ),
        )
        setup_bat = self.archive_dir / "setup.bat"
        setup_bat.write_text(content, "ansi")
        return setup_bat

    def create_installer_cfg(self, run_program: str) -> Path:
        content = self.installer_cfg.read_text("utf-8")
        content = content.replace("{title}", self.sfx_title).replace("{run_program}", run_program)
        installer_cfg = self.build_dir / "installer.cfg"
        installer_cfg.write_text(content, "utf-8")
        return installer_cfg

    def copy_files(self) -> None:
        project_dir = self.project_dir
        archive_dir = self.archive_dir
        for file in self.files:
            if isinstance(file, tuple):
                src, dst = (Path(f) for f in file)
            else:
                src = Path(file)
                dst = Path(src.name)
            if not src.is_absolute():
                src = project_dir / src
            if not dst.is_absolute():
                dst = archive_dir / dst
            if not src.exists():
                raise FileNotFoundError(src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    def create_sfx_installer(self) -> Path:
        build_dir = self.build_dir
        archive_dir = self.archive_dir
        dist_dir = self.dist_dir
        whl_file = self.whl_file
        setup_bat = self.create_setup_bat()
        installer_cfg = self.create_installer_cfg(setup_bat.name)
        assert whl_file.parent == archive_dir, (
            f"File {whl_file} is not in the archive directory {archive_dir}"
        )
        
        # Create the archive
        archive_7z = build_dir / "archive.7z"
        cmd = [
            str(self._7Z_EXE),
            "a",
            "-t7z",
            str(archive_7z.relative_to(archive_dir, walk_up=True)),
            *(str(file.relative_to(archive_dir)) for file in walk(archive_dir)),
            "-m0=BCJ2",
            "-m1=LZMA:d25:fb255",
            "-m2=LZMA:d19",
            "-m3=LZMA:d19",
            "-mb0:1",
            "-mb0s1:2",
            "-mb0s2:3",
            "-mx",
        ]
        subprocess.run(cmd, check=True, cwd=archive_dir)
        # Create the setup executable
        cmd = [
            "copy",
            "/b",
            str(self._7ZSD_SFX),
            "+",
            str(installer_cfg),
            "+",
            str(archive_7z),
            "setup.exe",
        ]
        subprocess.run(cmd, shell=True, check=True, cwd=build_dir)
        dist_setup_exe = dist_dir / "setup.exe"
        dist_setup_exe.unlink(missing_ok=True)
        shutil.move(build_dir / "setup.exe", dist_setup_exe)
        return dist_setup_exe

    def build(self) -> Path:
        """Build the setup."""
        build_dir = self.build_dir
        archive_dir = self.archive_dir
        dist_dir = self.dist_dir
        for dir_ in (build_dir, archive_dir, dist_dir):
            if dir_.exists():
                shutil.rmtree(dir_)
            dir_.mkdir(parents=True)
        self.build_whl()
        self.copy_files()
        return self.create_sfx_installer()


if __name__ == "__main__":
    setup = Setup(
        files=[
            BASE_DIR / "bootstrap.py",
            BASE_DIR / "pip.ini.template",
            BASE_DIR / "loader.lsp.template",
            BASE_DIR / "loader.py",
        ],
        bootstrap_args=(
            "%localappdata%\\Programs\\PyRx-sample-project",  # install_dir
            "{whl_file}",
            "--onload_file",
            "loader.py",
        ),
    )
    setup_exe = setup.build()
    print(f"Installer built: {setup_exe}")
