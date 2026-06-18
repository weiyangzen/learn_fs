# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdgbr.c

Ghostscript default implementation of `get_bits` and `get_bits_rectangle`, including conversion between native device pixels and requested standard bitmap formats.

Key behavior:
- `gx_default_get_bits` delegates single-scanline reads to `get_bits_rectangle` while temporarily disabling itself to avoid recursion.
- `requested_includes_stored` checks whether stored bitmap options satisfy a caller’s requested packing/color/depth/alpha format.
- `gx_get_bits_return_pointer` attempts zero-copy pointer returns when alignment, raster, packing, and plane-selection constraints allow it.
- `gx_get_bits_copy` copies or transforms bitmap regions into requested chunky/planar destination buffers.
- Supports direct bit-copy, unaligned bit-copy through memory-device `copy_mono`, chunky-to-planar extraction, native-to-standard conversion, and standard-to-native conversion.
- Special-cases 1-bit-per-component CMYK to 24-bit RGB conversion.
- `gx_default_get_bits_rectangle` bridges devices that only implement `get_bits`, handles partial-row extraction, and otherwise processes rectangles row by row through `gx_get_bits_copy`.

Notable dependencies:
- Ghostscript bitmap option and sample-load/store macros: `gxgetbit.h`.
- Memory devices and bitmap helpers: `gxdevmem.h`, `gdevmem.h`.
- Luminance weights from `gxlum.h`.

Research notes:
- This file is device raster plumbing, not filesystem code.
- Much of the complexity comes from honoring many combinations of return mode, packing mode, offset, raster, color space, depth, alpha, and plane selection.
- The implementation intentionally uses temporary recursion guards by swapping device procedure pointers during fallback calls.
- Some paths only support `GB_DEPTH_8` for native-to-standard conversion and return rangecheck for unsupported format combinations.
