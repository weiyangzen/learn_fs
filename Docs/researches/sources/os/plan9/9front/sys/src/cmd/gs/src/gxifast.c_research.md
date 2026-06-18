# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxifast.c

## Role

`gxifast.c` implements fast rendering paths for simple 1-bit-per-sample monochrome images in portrait or landscape orientation.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_class_1_simple`: class selector for fast monobit rendering.
- `image_render_skip`: skips completely transparent images.
- `image_render_simple`: fast portrait/no-rotation monobit renderer.
- `image_render_landscape`: fast 90-degree rotated monobit renderer.

## Important Algorithms

- `gs_image_class_1_simple` only selects this path when there is no RasterOp, `spp == 1`, `bps == 1`, and posture is portrait or landscape.
- It replaces unpacking with `sample_unpack_copy`, configures line buffers when scaling/rotation needs them, and handles mask-color transparency by making one image color transparent or by selecting the skip renderer.
- `image_simple_expand` scales one input monobit row into an output bitmap row using fixed-point DDAs, run scanning, byte run-length lookup tables, and byte/bit masks.
- `copy_portrait` chooses between direct `copy_mono` for pure colors and `fill_masked`/background fill for non-pure or transparent device colors.
- `image_render_simple` can directly expand into a memory device bitmap for the common pure-color, unclipped, positive-scale case; otherwise it expands into a buffer and copies each output row.
- `image_render_landscape` buffers 8 scan-line groups, flips them with `memflip8x8`, and then copies the rotated block through the portrait copy path.

## Dependencies And Integration

- Uses `gsbittab` lookup tables, bitmap alignment constants, Ghostscript DDA macros, image enumerator fields, memory device internals, device color loading, `copy_mono`, and masked-fill device color methods.
- Uses `gzht.h` indirectly through included image/device infrastructure.

## Notable Risks

- This path is highly optimized and depends on bitmap alignment, byte bit ordering, and DDA rounding details.
- There are compiler-workaround comments around DDA step computations, indicating sensitivity to generated code.
- The direct-memory-device path writes into scan-line storage and preserves edge bytes manually; clipping and bounds checks are intentionally strict before using it.
- Statistics code is enabled under DEBUG and changes macro behavior only for counters, not rendering.
