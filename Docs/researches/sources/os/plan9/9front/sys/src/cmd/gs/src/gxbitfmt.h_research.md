# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitfmt.h

Defines bit-mask descriptors for flexible bitmap storage and transfer formats.

Key definitions:
- `gx_bitmap_format_t` is an option bitmask.
- Color alternatives include native device pixels, DeviceGray, DeviceRGB, and DeviceCMYK.
- Alpha alternatives include none, first component, and last component.
- Supported per-component depths are 1, 2, 4, 8, 12, and 16 bits, with macros to derive maximum or exact depth from an option mask.
- Packing alternatives include chunky, planar, and bit-planar forms.
- Options describe plane selection, return by copy or pointer, alignment requirements, X offset constraints, and raster constraints.
- Provides string-name macro lists for debug output.

Research notes:
- Comments note planar and especially bit-planar formats are only partially supported.
- Several options only make sense for `GB_RETURN_POINTER`; copy callers must know offsets/rasters to size buffers correctly.
