# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcldev.h

Central internal header for Ghostscript command-list writer/reader support.

Key definitions:
- Defines bitmap compression mode constants for RLE and CCITTFax encoding plus initialization functions for encoder/decoder stream states.
- Defines the primary command bytecode enum: misc commands, tile setup, bitmap setup, color changes, rectangle fills/tiles, mono/color/alpha copies, and tile-index deltas.
- Defines debug opcode-name tables when `DEBUG` is enabled.
- Defines variable-size integer sizing and writing macros used throughout command-list emitters.
- Defines rectangle operand structures, short/tiny rectangle ranges, and encoded tile-depth conversion supporting depths above 32 bits.
- Documents and declares `clist_bitmap_bytes`.
- Defines `cmd_block` entries for band-file positions.
- Defines `gx_clist_state_s`, the per-band state cache for colors, saved device color, tile id/index/phase/colors, last rectangle, RasterOp, clip/logical-op flags, alpha-copy mode, known-state bitmask, command list, rendering cost, and colors-used accounting.
- Provides `cls_initial_values` for band-state initialization and `cbuf_size` for reader command buffer sizing.
- Declares clist device procedures implemented by rectangle, image/compositor, and reader modules.
- Declares writer-side VM-error recovery functions for asynchronous rendering and documents the two-stage recovery process.
- Defines command-allocation macros for per-band, range, and all-band commands plus command shortening.
- Declares color, tile, logical-op, clip, rectangle, bitmap, color-map, color-mapping, halftone, and playback helpers.
- Defines `FOR_RECTS`, `TRY_RECT`, `HANDLE_RECT`, and related macros that split drawing operations by band and coordinate retry/flush recovery.

Dependencies:
- Includes command-list device structures, RasterOp types, halftone/transfer-map/device-halftone headers, compression stream internals, and drawing-color definitions.

Research notes:
- This header is effectively the ABI for command-list bytecode writers and readers; small encoding changes affect many implementation files.
- The recovery macros are deliberately not transparent: callers must keep writer state idempotent until successful command emission.
- `known` flags are partitioned with path code; this header allocates high bits for tile and image state.
