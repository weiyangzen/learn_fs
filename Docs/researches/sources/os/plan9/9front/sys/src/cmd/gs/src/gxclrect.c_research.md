# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrect.c

Rectangle-oriented command-list writer operations.

Key behavior:
- Encodes rectangles compactly with full, short-delta, tiny-delta, and special adjacent rectangle forms through `cmd_write_rect_cmd`.
- Implements clist writer device procedures for `fill_rectangle`, `strip_tile_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, and `strip_copy_rop`.
- Tracks colors used per band and updates clist state for current colors, tile colors, tile phase, logical operation state, and clip state.
- Emits bitmap payloads with `cmd_put_bits`, choosing compression and splitting large transfers by height or row width when a payload cannot fit.
- Handles tile caching and tile ID lookup/change commands before tiled fills and ROP texture operations.
- Converts high-level RasterOp calls into clist state updates plus nested simpler fill/copy operations, while marking slow ROP cases for later render-plane selection.

Notable dependencies:
- Writer-side macros and state from `gxcldev.h`.
- Tile, bitmap, RasterOp, and color-command helpers from the clist infrastructure.
- Default device fallback procedures for cases too large or unsupported by the command buffer.

Research notes:
- The file is focused on producing compact command streams; much complexity is about command buffer limits and avoiding repeated state emission.
- Very large bitmaps or tiles are recursively split; some tile limit cases only split by scan line and punt if a single scan line cannot fit.
- CMYK RasterOps are conservatively marked slow when destination involvement makes plane-wise rendering unsafe.
