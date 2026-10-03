from typing import Callable, IO, cast
import itertools
from fractions import Fraction
from PIL import Image, ImageFile, ImageSequence, PngImagePlugin
from PIL.PngImagePlugin import _Frame, _idat, _fdat, o8, o16, o32, Disposal, Blend

def full_frame_write_multiple_frames(
    im: Image.Image,
    fp: IO[bytes],
    chunk: Callable[..., None],
    mode: str,
    rawmode: str,
    default_image: Image.Image | None,
    append_images: list[Image.Image],
) -> Image.Image | None:
    duration = im.encoderinfo.get("duration", 100)
    loop = im.encoderinfo.get("loop", im.info.get("loop", 0))
    # LINE公式規定: 全フレーム同一サイズ(320x270)、dispose_op=APNG_DISPOSE_OP_BACKGROUND (2)、blend_op=APNG_BLEND_OP_SOURCE (0)
    disposal = Disposal.OP_BACKGROUND
    blend = Blend.OP_SOURCE

    if default_image:
        chain = itertools.chain(append_images)
    else:
        chain = itertools.chain([im], append_images)

    im_frames: list[_Frame] = []
    frame_count = 0
    full_bbox = (0, 0) + im.size

    for im_seq in chain:
        for im_frame in ImageSequence.Iterator(im_seq):
            if im_frame.mode == mode:
                im_frame = im_frame.copy()
            else:
                im_frame = im_frame.convert(mode)
            encoderinfo = im.encoderinfo.copy()
            if isinstance(duration, (list, tuple)):
                encoderinfo["duration"] = duration[frame_count]
            elif duration is None and "duration" in im_frame.info:
                encoderinfo["duration"] = im_frame.info["duration"]
            encoderinfo["disposal"] = disposal
            encoderinfo["blend"] = blend
            frame_count += 1
            # 差分クロップを行わず、常にフルサイズ (320x270) を保証！
            im_frames.append(_Frame(im_frame, full_bbox, encoderinfo))

    if len(im_frames) == 1 and not default_image:
        return im_frames[0].im

    chunk(
        fp,
        b"acTL",
        o32(len(im_frames)),
        o32(loop),
    )

    if default_image:
        default_im = im if im.mode == mode else im.convert(mode)
        _apply_encoderinfo(default_im, im.encoderinfo)
        ImageFile._save(
            default_im,
            cast(IO[bytes], _idat(fp, chunk)),
            [ImageFile._Tile("zip", (0, 0) + im.size, 0, rawmode)],
        )

    seq_num = 0
    for frame, frame_data in enumerate(im_frames):
        im_frame = frame_data.im
        bbox = full_bbox
        size = im_frame.size
        encoderinfo = frame_data.encoderinfo
        frame_duration = encoderinfo.get("duration", 100)
        delay = Fraction(frame_duration / 1000).limit_denominator(65535)
        
        chunk(
            fp,
            b"fcTL",
            o32(seq_num),
            o32(size[0]),
            o32(size[1]),
            o32(bbox[0]),
            o32(bbox[1]),
            o16(delay.numerator),
            o16(delay.denominator),
            o8(disposal),
            o8(blend),
        )
        seq_num += 1
        
        PngImagePlugin._apply_encoderinfo(im_frame, im.encoderinfo)
        if frame == 0 and not default_image:
            ImageFile._save(
                im_frame,
                cast(IO[bytes], _idat(fp, chunk)),
                [ImageFile._Tile("zip", (0, 0) + im_frame.size, 0, rawmode)],
            )
        else:
            fdat_chunks = _fdat(fp, chunk, seq_num)
            ImageFile._save(
                im_frame,
                cast(IO[bytes], fdat_chunks),
                [ImageFile._Tile("zip", (0, 0) + im_frame.size, 0, rawmode)],
            )
            seq_num = fdat_chunks.seq_num
    return None

# モンキーパッチ適用
PngImagePlugin._write_multiple_frames = full_frame_write_multiple_frames
print("Successfully installed full_frame_write_multiple_frames patch!")
