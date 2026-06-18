# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevabuf.c

## Scope

Alpha memory devices and alpha-buffering device for antialiased rasterization.

## Key Behavior

- `gs_make_mem_alpha_device` creates 2-bit or 4-bit alpha devices that behave like black/white for color mapping but store multiple bits per pixel.
- Alpha color mapping forwards to the target device and converts nonzero colors into alpha levels.
- `gs_make_mem_abuf_device` creates an oversampled monobit buffer that compresses accumulated bits into alpha scanlines for a lower-resolution target.
- Maintains a sliding mapped Y window to avoid copying band storage as rendering advances.
- Flushes full alpha blocks with `bits_bounding_box`, `bits_compress_scaled`, and target `copy_alpha`.
- Implements `copy_mono`, `fill_rectangle`, close/flush, and scaled clipping-box behavior.

## Dependencies

Uses Ghostscript memory-device internals, bitmap compression/scaling helpers, forwarding color mapping, and target `copy_alpha`.

## Risks And Invariants

- Client rendering must visit bands mostly top-to-bottom and not repaint arbitrary old bands.
- Buffer height must be compatible with Y scale; blocks flush at scale-factor boundaries.
- Only single-color output is supported; `save_color` carries the target color through flush.
