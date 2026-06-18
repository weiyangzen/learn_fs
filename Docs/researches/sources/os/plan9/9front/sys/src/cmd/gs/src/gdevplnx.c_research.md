# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevplnx.c

Implementation of Ghostscript's plane extraction forwarding device. A plane extraction device appears like the original target device but reduces drawing into a selected bit plane and forwards reduced operations to a plane device, normally a memory device used by planar printer band rendering.

Key behavior:
- Defines the `gs_plane_extract_device` prototype, GC relocation/enumeration hooks, and driver procedures for rectangles, masks, paths, images, RasterOps, tiles, alpha copies, and get-bits.
- `plane_device_init` initializes forwarding-device state, copies target parameters, stores the plane target, opens plane extraction state, and optionally clears the plane device to white.
- `plane_open_device` derives `plane_white`, `plane_mask`, and whether the plane device is memory-like.
- `COLOR_PIXEL` and `TRANS_COLOR_PIXEL` extract the selected plane bits from chunky `gx_color_index` values.
- `reduce_drawing_color` rewrites pure, binary-halftone, and colored-halftone drawing colors into plane-local colors and skips early all-white drawing until any non-white mark has appeared.
- Rectangle, monochrome, alpha, path, stroke, mask, parallelogram, and triangle handlers either skip white-only work, forward reduced operations, or fall back to Ghostscript defaults when reduction is unsafe.
- `begin_tiling`, `extract_partial_tile`, `next_tile`, and `end_tiling` split chunky source tiles into temporary plane tiles using `bits_extract_plane`, with stack buffers first and heap buffers when needed.
- `plane_copy_color`, `plane_strip_tile_rectangle`, and `plane_strip_copy_rop` extract planes from source/texture pixmaps and forward them to the underlying plane device, falling back for transparent RasterOps.
- `plane_begin_typed_image` wraps image rendering with modified color-map procs so image colors are reduced before the plane device sees them.
- `plane_get_bits_rectangle` supports selected planar retrieval and can also expand the single plane back into chunky pixels with `bits_expand_plane`.

Notable dependencies:
- Ghostscript device, memory, clist/image, color, halftone, RasterOp, bit-plane, and get-bits APIs: `gxdevice.h`, `gxdevmem.h`, `gxgetbit.h`, `gxiparam.h`, `gxistate.h`, `gxrplane.h`, `gsrop.h`, `gxdither.h`.
- Public interface and state definition from `gdevplnx.h`.

Research notes:
- The `any_marks` optimization is central: before a plane has any non-white marks, white-only operations are discarded.
- The code deliberately punts to default implementations when transparency or RasterOp semantics require full-pixel context.
- In `begin_tiling`, the partial-buffer branch computes a smaller raster/width when the local buffer cannot hold a full row, but then unconditionally resets `pts->buffer.raster = width_raster`; that looks inconsistent with the immediately preceding partial-width calculation.
- In `plane_strip_copy_rop`, the source tiling call passes `w, y` as width/height, which appears suspicious because the requested height is `h`; this may be a typo with visible effects for copied RasterOp sources.
