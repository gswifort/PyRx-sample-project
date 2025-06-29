from pathlib import Path

from pyrx import command
from pyrx.console import console
from pyrx.utils.test_runner import FileTestArgsProvider, PytestTestRunner

BASE_DIR = Path(__file__).parent
runner = PytestTestRunner(
    modules_to_reload=("pyrx_sample_project", "tests"),
    test_args_provider=FileTestArgsProvider(BASE_DIR / "test_args.txt"),
)


@command
def run_tests():
    with console(allow_existing=False):
        runner.start()
        input("Press any key to exit...")
