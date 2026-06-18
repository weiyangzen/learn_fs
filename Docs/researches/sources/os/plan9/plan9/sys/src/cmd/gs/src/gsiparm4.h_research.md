# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiparm4.h

Defines ImageType 4 image parameters.

`gs_image4_t` extends pixel image common data with:
- `MaskColor_is_range`
- `MaskColor[GS_IMAGE_MAX_COMPONENTS * 2]`

Semantics:
- If `MaskColor_is_range` is false, the first N entries are exact sample values.
- If true, the first 2*N entries are ranges.
- Current library support is noted as up to 12-bit samples, with eventual DevicePixel support for wider samples.

Exports descriptor macro and `gs_image4_t_init`.

Default documented:
- `MaskColor_is_range = false`
