# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage4.c

Ghostscript ImageType 4 implementation for color-key masked images.

Key behavior:
- Defines `gs_image_type_4`, using the same lower-level enumerator/rendering machinery as ImageType 1.
- Initializes ImageType 4 objects with a color space and default non-range `MaskColor`.
- `gx_begin_image4` allocates the shared image enumerator, validates `MaskColor` values against `BitsPerComponent`, normalizes exact or ranged mask colors into enumerator ranges, and disables masking if a range is impossible.
- Delegates rendering setup to `gx_image_enum_begin`.
- Serializes/deserializes generic pixel image parameters plus MaskColor values; the generic extra control bit stores `MaskColor_is_range`.

Notable dependencies:
- Public ImageType 4 parameters from `gsiparm4.h`.
- Shared image pipeline from `gximage.h`.
- Stream helpers from `stream.h`.

Research notes:
- Out-of-range mask colors produce `rangecheck`.
- If a mask-color range has `c0 > c1`, the implementation treats the image as fully opaque because no pixel can match that range.
