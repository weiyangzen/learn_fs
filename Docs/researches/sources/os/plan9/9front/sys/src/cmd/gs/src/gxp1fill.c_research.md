# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxp1fill.c

PatternType 1 rectangle filling algorithms for Ghostscript.

Key behavior:
- Defines `tile_fill_state_t`, carrying original fill arguments, tile/mask clip setup, phase, RasterOp source state, and offsets for non-simple tiles.
- `tile_fill_init` initializes optional tile mask clipping and computes mask phase for simple masked tiles.
- `tile_by_steps` handles non-standard pattern step matrices by transforming the filled rectangle into pattern step space, iterating all overlapping tile placements, clipping each tile copy, updating mask phase/offsets, and calling a supplied fill callback.
- `tile_colored_fill` fills a clipped piece of a colored pattern using either `copy_color` or `strip_copy_rop`.
- `gx_dc_pattern_fill_rectangle` handles colored Pattern fills, choosing fast simple-tile paths or `tile_by_steps` for non-simple patterns.
- `tile_masked_fill` adapts source offsets for uncolored masked pattern pieces.
- `gx_dc_pure_masked_fill_rect`, `gx_dc_binary_masked_fill_rect`, and `gx_dc_colored_masked_fill_rect` wrap pure, binary halftone, and colored halftone rectangle fills with mask-tile handling.

Notable dependencies:
- Pattern/color definitions from `gxpcolor.h` and `gxp1impl.h`.
- Tile clipping from `gxclip2.h`.
- Device color and RasterOp APIs from `gxdcolor.h`, `gxdevcli.h`, and `gsrop.h`.

Research notes:
- Non-simple pattern tiling is intentionally conservative for partly transparent patterns, expanding the iteration range so every overlapping pattern copy affects the fill.
- A local comment questions a possible leak/memory pointer choice in `tile_fill_init`; the call currently passes `dev->memory` to `tile_clip_initialize`.
