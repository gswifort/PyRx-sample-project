import traceback
from pathlib import Path

from pyrx import Ap

BASE_DIR = Path(__file__).parent


def OnPyInitApp():
    try:
        Ap.Application.loadPythonModule(str(BASE_DIR / "testrunner.py"))
    except Exception:
        traceback.print_exc()
