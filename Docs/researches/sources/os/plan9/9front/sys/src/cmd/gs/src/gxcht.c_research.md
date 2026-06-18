# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcht.c

Implements colored halftone device colors: serialization/deserialization, equality/saved-state support, nonzero-component reporting, color table setup, and raster composition for halftoned rectangle fills.

Key behavior:
- Defines `gx_dc_type_ht_colored`, including save, device-halftone access, load, fill-rectangle, equality, write/read, and nonzero-component procedures.
- Saves and compares colored halftone device colors by halftone pointer, alpha, phase, component count, base component values, and halftone level values.
- Serializes colored halftone device colors using flag bits for base values, level values, and alpha; omits unchanged fields by comparing against the previous saved device color.
- Optimizes serialization for 1-bit-per-component devices by packing base component bits into bytes.
- Serializes level values using `plane_mask` so only nonzero halftoned components are transmitted; supports component masks wider than a native `uint`.
- Reconstructs colored halftone device colors from serialized data, using the current imager state's device halftone and screen phase.
- Reports nonzero components as the union of `plane_mask` and components with nonzero base values.
- Fills rectangles by clipping to the device box, clearing transparent RasterOp texture semantics, loading per-plane halftone caches, choosing optimized color and tile-composition procedures, and then either tiling an LCM-sized cell or generating smaller chunks.
- Supports no-source copy paths through `copy_color`/`strip_tile_rectangle`, and RasterOp paths through `strip_copy_rop`.
- Builds color lookup tables differently for <=4 planes, special 1-bit CMYK, and >4 planes.
- For subtractive color models, inverts color pairs and halftone levels so additive halftone orders can drive subtractive devices.
- Uses a special 1-bit CMYK path that reverses planes and computes packed pixels through Boolean masks rather than per-pixel lookup.
- For >4 components, assumes separable device color indices and combines per-plane encoded values with bitwise OR.
- Renders halftone tiles through per-plane `tile_cursor_t` objects that handle X offset, wrapping, shifted tiles, row stepping, and packed output for 4/8/16/24/32-bit depths.

Dependencies:
- Uses device color interfaces from `gxdcolor.h`, halftone internals from `gzht.h`, device color mapping from `gxcmap.h`, device procedures, fixed/matrix helpers, and `gs_next_ids`.

Research notes:
- The implementation has multiple explicit optimization tiers: small component-count lookup tables, 1-bit CMYK bit masks, and a separable fallback for DeviceN-like cases.
- Several comments mark limitations for DeviceN, alpha, and extra planes; these paths should be treated as pragmatic support for the command-list era rather than a fully general color architecture.
- The fill path assumes colored halftones are opaque texture for RasterOp by clearing `lop_T_transparent`.
