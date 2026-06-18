# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxifast.c

Purpose: provides fast rendering paths for simple 1-bit monochrome images.

Strategy:
- `gs_image_class_1_simple` selects this path only for non-ROP, single-component, 1-bit images.
- Supports portrait and 90-degree landscape postures.
- Allocates line buffers when scaling or landscape rotation requires intermediate storage.
- Sets `sample_unpack_copy` and adjusts unpack state so raw bits can be consumed directly.
- Converts mask-color ranges into transparent `gx_no_color_index` device colors, or skips completely transparent images.

Core rendering:
- `image_render_skip`: consumes transparent image data without drawing.
- `image_simple_expand`: scales and optionally reverses one monobit scan line using fixed-point DDA state and run scanning.
- `copy_portrait`: copies expanded bits to the target, using `copy_mono` for pure colors or masked fills when one color is non-pure/transparent.
- `image_render_simple`: optimized portrait renderer, including direct memory-device bitmap expansion when conditions are safe.
- `image_render_landscape`: buffers groups of 8 scan lines for 90-degree rotated images.
- `copy_landscape`: flips 8x8 blocks with `memflip8x8` and copies them through the portrait path.

Dependencies:
- Uses bit tables, fixed-point DDA math, device color loading, memory-device internals, clipping constraints, and halftone/device color fill hooks.

Research notes:
- The direct memory-device fast path carefully saves/restores edge bytes outside the image bounds.
- Landscape rendering flushes buffered data on discontinuities, end-of-input, or explicit flush calls.
