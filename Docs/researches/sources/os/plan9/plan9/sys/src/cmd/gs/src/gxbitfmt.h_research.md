# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitfmt.h

Purpose: Defines bitmask flags describing bitmap storage/transfer formats for procedures such as `get_bits_rectangle`.

Key definitions:
- `gx_bitmap_format_t` is a bitmask type.
- Color alternatives: native, Gray, RGB, CMYK.
- Alpha alternatives: none, first component, last component.
- Component depths: 1, 2, 4, 8, 12, 16.
- Packing alternatives: chunky, planar, bit-planar.
- Plane selection, return method, alignment, x-offset, and raster flags.
- Debug names aggregate via `GX_BITMAP_FORMAT_NAMES`.

Behavior:
- `GB_OPTIONS_MAX_DEPTH()` and `GB_OPTIONS_DEPTH()` extract depth information from masks.
- `GB_RETURN_POINTER` makes alignment, offset, and raster looseness meaningful; `GB_RETURN_COPY` generally requires caller-specified layout.

Dependencies:
- Requires `ulong`.

Notable risks:
- Some formats are explicitly only partially supported, especially planar and bit-planar packing.
- Bit assignments consume up to bit 30, so extension space in this mask is limited.
