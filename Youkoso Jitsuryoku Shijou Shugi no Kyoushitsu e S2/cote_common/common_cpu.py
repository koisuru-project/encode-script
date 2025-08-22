from __future__ import annotations

from pathlib import Path

from muxtools import Setup, VideoFile
from muxtools import mux as vsmux
from pydantic import BaseModel, ConfigDict
from vodesfunc import adaptive_grain, ntype4
from vsdeband import f3k_deband
from vskernels import Bilinear
from vsmasktools import dre_edgemask
from vsmlrt import Backend
from vsmuxtools import (
    FLAC,
    Resample,
    do_audio,
    settings_builder_x265,
    src_file,
    x265,
)
from vspreview import is_preview
from vsscale import ArtCNN, Rescale
from vstools import (
    FrameRangeN,
    FrameRangesN,
    depth,
    finalize_clip,
    replace_ranges,
    set_output,
    vs,
)

from cote_common.common_modules_cpu import bore, denoise, handle_lerche_chroma
from cote_common.sources import Source


class FilterchainResults(BaseModel):
    src: vs.VideoNode
    final: vs.VideoNode
    audio_file: src_file

    model_config = ConfigDict(arbitrary_types_allowed=True)


def filterchain(
    *,
    source: Source,
    no_descale: FrameRangeN | FrameRangesN = None | None,
    credits_mask: FrameRangeN | FrameRangesN = None | None,
    chroma_ignore: FrameRangeN | FrameRangesN = None | None,
    border_ranges: FrameRangeN | FrameRangesN = None | None,
) -> FilterchainResults:
    """
    Main video processing filterchain with multiple source handling and advanced filtering.
    """
    # Load source file
    JPBD = src_file(str(source.JPBD), trim=(source.src_cut[0], source.src_cut[1] + 1))
    src = JPBD.init_cut().std.SetFrameProps(source="JPBD")
    border = bore(src, ranges=border_ranges)

    # Native resolution configuration
    native_res = dict(
        width=1280,
        height=720,
    )

    # Rescaling with conditional handling
    rs = Rescale(
        depth(border, 32),
        kernel=Bilinear(),
        upscaler=ArtCNN.R8F64(backend=Backend.OV_CPU(bf16=True)),
        **native_res,
    )

    # Generate masks
    credits = rs.default_credit_mask(thr=0.216, expand=4, ranges=credits_mask)
    rs.default_line_mask()

    # Handle no_descale ranges
    if no_descale:
        upscaled = replace_ranges(depth(rs.upscale, 16), src, no_descale)
    else:
        upscaled = depth(rs.upscale, 16)

    # Denoise with improved settings
    dns = denoise(upscaled, sigma=[0.7, 0.25])

    # Handle chroma processing sections
    chroma = handle_lerche_chroma(dns, use_eedi3=True)
    chromaign = replace_ranges(chroma, upscaled, chroma_ignore)

    # Advanced debanding
    deband = f3k_deband(
        chromaign, radius=16.0, thr=[3.0, 3.5, 3.0], grain=[0.2, 0.1, 0.2]
    )
    mask = dre_edgemask.RETINEX(chromaign, brz=10 / 255)
    deband = deband.std.MaskedMerge(chromaign, mask)

    # Adaptive grain application
    grain = adaptive_grain(
        deband,
        strength=[1.9, 0.4],
        size=3.3,
        temporal_average=50,
        seed=217404,
        **ntype4,
    )

    # Finalize clip
    final = finalize_clip(grain, 10, False)

    # Preview outputs
    if is_preview():
        set_output(src, "src")
        set_output(credits)
        set_output(final, "final")

    return FilterchainResults(src=src, final=final, audio_file=JPBD)


def mux_video(
    *,
    episode: str,
    source: Source,
    filterchain_results: FilterchainResults,
) -> Path | str:
    """
    Mux video and audio with advanced x265 settings.
    """
    setup = Setup(
        episode,
        None,
        allow_binary_download=False,
        mkv_title_naming="$show$ - $ep$",
        out_dir="output",
        out_name="[premux] $show$ - $ep$ (BDRip 1920x1080 HEVC FLAC) [#crc32#]",
        show_name="Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e S2",
    )
    assert setup.work_dir

    # Advanced x265 encoding settings
    settings = settings_builder_x265(
        preset="placebo",
        crf=13,
        qcomp=0.73,
        bframes=12,
        rd=3,
        rect=False,
        ref=5,
        keyint=round(filterchain_results.final.fps) * 10,
    )

    # Prepare encoding zones for OP/ED
    encoded = Path(setup.work_dir).joinpath("encoded.265").resolve()
    zones: list[tuple[int, int, float]] = []

    if hasattr(source, "op") and source.op is not None:
        zones.append((source.op[0], source.op[1], 1.2))
    if hasattr(source, "ed") and source.ed is not None:
        zones.append((source.ed[0], source.ed[1], 1.2))

    # Create or use existing encoded video
    video = (
        VideoFile(encoded)
        if encoded.exists()
        else x265(
            settings, zones=zones, qp_clip=filterchain_results.src, resumable=False
        ).encode(filterchain_results.final)
    )

    # Mux final output
    return vsmux(
        video.to_track(
            "BD encode by Masih Pemula",
            "jpn",
            default=True,
            forced=False,
        ),
        do_audio(
            filterchain_results.audio_file,
            track=0,
            encoder=FLAC(preprocess=Resample(depth=None)),
        ).to_track("FLAC 2.0", "jpn", default=True, forced=False),
    )
