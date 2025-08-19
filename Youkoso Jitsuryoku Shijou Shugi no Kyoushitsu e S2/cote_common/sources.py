from __future__ import annotations

from pathlib import Path, PurePath

from pydantic import BaseModel

RAWS_DIRECTORY = Path(r"C:\Users\ao\Downloads")


class Source(BaseModel):
    JPBD: PurePath | str
    src_cut: tuple[int, int] | None = None
    op: tuple[int, int] | None = None
    ed: tuple[int, int] | None = None


sources = {
    "01": Source(
        JPBD=RAWS_DIRECTORY / "00004.m2ts",
        src_cut=(24, 34048),
        op=(1607, 1607 + 2156 + 1),  # 3764
        ed=(31890, 31890 + 2156 - 22),  # 34024
    ),
}
