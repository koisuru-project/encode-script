from __future__ import annotations

from cote_common import filterchain, mux_video, sources
from vspreview import is_preview

EPISODE = "01"
source = sources[EPISODE]
NO_DESCALE = []
BORDER_RANGES = []
CREDITS_MASK = [source.ed]
CHORMA_IGNORE = [source.op]

filterchain_results = filterchain(
    source=source,
    border_ranges=BORDER_RANGES,
    no_descale=NO_DESCALE,
    credits_mask=CREDITS_MASK,
    chroma_ignore=CHORMA_IGNORE,
)

if not is_preview():
    mux_video(episode=EPISODE, source=source, filterchain_results=filterchain_results)
