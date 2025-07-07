import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).parent
LIB_DIR = BASE_DIR / "_internal"


def OnPyInitApp():
    try:
        if (lib_dir_str := str(LIB_DIR)) not in sys.path:
            sys.path.append(lib_dir_str)
        import pyrx_sample_project.cmds  # noqa: F401
    except Exception:
        traceback.print_exc()
