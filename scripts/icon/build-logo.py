"""Compatibility entry point. Export the supplied AlgorithVideo brand assets."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("export-assets.py")), run_name="__main__")
