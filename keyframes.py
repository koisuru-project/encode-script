from pathlib import Path

from vstools import Keyframes, core

src = core.ffms2.Source(r"")


keyframes = Path("./").joinpath("keyframes.txt").resolve()
if keyframes.exists():
    None
else:
    Keyframes.from_clip(src).to_file("keyframes.txt")
