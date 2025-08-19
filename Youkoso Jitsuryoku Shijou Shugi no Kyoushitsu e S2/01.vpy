from __future__ import annotations

from cote_common import filterchain, mux_video, sources
from vspreview import is_preview

EPISODE = "01"
source = sources[EPISODE]
NO_DESCALE = [
    source.ed,
]

filterchain_results = filterchain(source=source, no_descale=NO_DESCALE)

if not is_preview():
    mux_video(episode=EPISODE, source=source, filterchain_results=filterchain_results)
