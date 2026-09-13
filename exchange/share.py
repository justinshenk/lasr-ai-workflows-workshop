"""Thin wrapper: share from inside this repo. Same as the plugin's share.py with defaults set.
    uv run python exchange/share.py <your-name> [--push]
"""
import runpy, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], *sys.argv[1:], "--project", str(HERE.parent), "--exchange", str(HERE.parent)]
runpy.run_path(str(HERE.parent / "plugins" / "lasr-exchange" / "scripts" / "share.py"), run_name="__main__")
