from __future__ import annotations

import shutil
import subprocess
import sys
import typing as t
from pathlib import Path

if t.TYPE_CHECKING:
    import _typeshed as _t

BASE_DIR = Path(__file__).parent


def quote_path(__path: Path, /):
    return str(__path).replace("\\", "\\\\")


class Bootstrap:
    def __init__(
        self,
        install_dir: _t.StrPath,
        whl_file: _t.StrPath,
        src_dir: _t.StrPath | None = None,
        loader_lsp_template: _t.StrPath | None = None,
        loader_lsp_dst: _t.StrPath | None = None,
        onload_file: _t.StrPath | None = None,
    ) -> None:
        # src_dir
        if src_dir is None:
            self.src_dir = BASE_DIR
        else:
            self.src_dir = Path(src_dir)
            if not self.src_dir.is_absolute():
                self.src_dir = BASE_DIR / src_dir
        # install_dir
        self.install_dir: Path = Path(install_dir)
        if not self.install_dir.is_absolute():
            raise ValueError("install_dir must be an absolute path")
        self.install_dir_internal = self.install_dir / "_internal"
        # pyrx_dir
        self.pyrx_dir: Path = self.install_dir_internal / "pyrx"
        # whl_file
        self.whl_file: Path = Path(whl_file)
        if not self.whl_file.is_absolute():
            self.whl_file = self.src_dir / self.whl_file
        # loader_lsp
        if loader_lsp_template is None:
            self.loader_lsp_template: Path = self.src_dir / "loader.lsp.template"
        else:
            self.loader_lsp_template = Path(loader_lsp_template)
            if not self.loader_lsp_template.is_absolute():
                self.loader_lsp_template = self.src_dir / self.loader_lsp_template
        if loader_lsp_dst is None:
            self.loader_lsp: Path = self.install_dir / "loader.lsp"
        else:
            self.loader_lsp = Path(loader_lsp_dst)
            if not self.loader_lsp.is_absolute():
                self.loader_lsp = self.install_dir / self.loader_lsp
        # onload_file
        if onload_file is None:
            self.onload_file: Path | None = None
        else:
            self.onload_file = Path(onload_file)
            if not self.onload_file.is_absolute():
                self.onload_file = self.src_dir / self.onload_file
            self.onload_file_dst: Path = self.install_dir / self.onload_file.name

    def create_install_dir(self) -> None:
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.install_dir_internal.mkdir(parents=True, exist_ok=True)

    def install_whl(self) -> None:
        subprocess.run(
            (
                sys.executable,
                "-m",
                "pip",
                "install",
                str(self.whl_file),
                "--target",
                str(self.install_dir_internal),
            ),
            check=True,
        )

    def copy_onload_file(self) -> None:
        if self.onload_file is not None:
            shutil.copy(self.onload_file, self.onload_file_dst)

    def create_loader_lsp(self):
        content = self.loader_lsp_template.read_text("utf-8")
        content = content.replace("{pyrx_dir}", quote_path(self.pyrx_dir))
        if self.onload_file is not None:
            content = f'{content}\n(adspyload "{quote_path(self.onload_file_dst)}")\n'
        self.loader_lsp.write_text(content, "ansi")

    def run(self) -> None:
        self.create_install_dir()
        self.install_whl()
        self.copy_onload_file()
        self.create_loader_lsp()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("install_dir", type=Path, help="The installation directory.")
    parser.add_argument("whl_file", type=Path, help="The wheel file to install.")
    parser.add_argument(
        "--src_dir",
        type=Path,
        default=None,
        help="The source directory (default: current directory).",
    )
    parser.add_argument(
        "--loader_lsp_template",
        type=Path,
        default=None,
        help="The template for the loader.lsp file (default: loader.lsp.template in src_dir).",
    )
    parser.add_argument(
        "--loader_lsp_dst",
        type=Path,
        default=None,
        help="The destination for the loader.lsp file (default: install_dir/loader.lsp).",
    )
    parser.add_argument(
        "--onload_file",
        type=Path,
        default=None,
        help="An optional file to load on CAD app startup (default: None).",
    )
    args = parser.parse_args()
    bootstrap = Bootstrap(
        install_dir=args.install_dir,
        whl_file=args.whl_file,
        src_dir=args.src_dir,
        loader_lsp_template=args.loader_lsp_template,
        loader_lsp_dst=args.loader_lsp_dst,
        onload_file=args.onload_file,
    )
    bootstrap.run()
