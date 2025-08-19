from __future__ import annotations

from vsaa import EEDI3, NNEDI3
from vsdenoise import (
    MVToolsPreset,
    Prefilter,
    bm3d,
    mc_degrain,
    nl_means,
)
from vsdenoise.blockmatch import BM3D
from vsdenoise.nlm import NLMeans
from vsexprtools import norm_expr
from vskernels import Point
from vstools import (
    ChromaLocation,
    SingleOrArr,
    core,
    join,
    split,
    vs,
)


def denoise(
    clip: vs.VideoNode,
    block_size: int = 64,
    limit: int | tuple[int | None, int | None] | None = None,
    refine: int = 3,
    sigma: SingleOrArr[float] = 0.7,
    sr: int = 2,
    strength: float = 0.2,
    thSAD: int | tuple[int, int] = 115,
    tr: int = 2,
) -> vs.VideoNode:
    ref = mc_degrain(  # type: ignore[call-overload]
        clip,
        prefilter=Prefilter.DFTTEST,
        preset=MVToolsPreset.HQ_SAD,
        blksize=block_size,
        thsad=thSAD,
        limit=limit,
        refine=refine,
    )

    denoised_luma = bm3d(
        clip,
        ref=ref,
        sigma=sigma,
        tr=tr,
        planes=0,
        backend=BM3D.Backend.CPU,
        profile=BM3D.Profile.HIGH,
    )
    denoised_luma = ChromaLocation.ensure_presence(
        denoised_luma, ChromaLocation.from_video(clip, strict=True)
    )

    return nl_means(
        denoised_luma,
        ref=ref,
        h=strength,
        tr=tr,
        a=sr,
        wmode=NLMeans.WeightMode.BISQUARE_HR,
        planes=[1, 2],
        backend=NLMeans.Backend.ISPC,
    )


def handle_lerche_chroma(src: vs.VideoNode, use_eedi3=True):
    y, u, v = split(src)

    point_scaler = Point()
    upscaler = EEDI3() if use_eedi3 else NNEDI3()

    processed_chroma = []

    for chroma in [u, v]:
        chroma_down = point_scaler.scale(chroma, 640, 540)
        chroma_shifted = point_scaler.scale(chroma, 640, 540, src_left=-1)

        chroma_combined = core.std.StackHorizontal(
            [
                core.std.Crop(chroma_shifted, left=1),
                core.std.Crop(chroma_down, left=639),
            ]
        )

        chroma_avg = norm_expr([chroma_down, chroma_combined], "x y + 2 /", vs.GRAY)
        chroma_upscaled = upscaler.scale(chroma_avg, 960, 540)
        processed_chroma.append(chroma_upscaled)

    return join([y, *processed_chroma])
