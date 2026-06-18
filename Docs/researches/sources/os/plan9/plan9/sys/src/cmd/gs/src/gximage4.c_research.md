# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage4.c

Ghostscript ImageType 4 implementation for color-key masked images.

Key behavior:
- Defines `gs_image_type_4`, reusing the lower-level ImageType 1 enumerator/rendering machinery.
- Initializes ImageType 4 images with a color space and non-range `MaskColor` mode by default.
- `gx_begin_image4` allocates the shared image enumerator, validates mask color values against `BitsPerComponent`, normalizes exact/ranged mask colors into enumerator ranges, and disables masking if a range is impossible.
- Delegates rendering setup to `gx_image_enum_begin`.
- Serializes/deserializes generic pixel image parameters plus `MaskColor` values; the generic extra control bit stores `MaskColor_is_range`.

Notable dependencies:
- Public ImageType 4 parameters from `gsiparm4.h`.
- Shared image pipeline from `gximage.h`.
- Stream helpers from `stream.h`.

Research notes:
- Out-of-range mask colors produce `rangecheck`.
- A `c0 > c1` mask range is treated as fully opaque because no source sample can match it.
