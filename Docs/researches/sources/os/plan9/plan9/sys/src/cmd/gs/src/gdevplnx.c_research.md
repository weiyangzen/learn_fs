# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevplnx.c

This file implements Ghostscript's plane extraction forwarding device. A plane extraction device presents the same color-capable interface as its target, but redirects rendering for one selected bit plane into a separate plane device, normally a memory device.

The core public initializer is `plane_device_init`, which clones the target device parameters, stores the target and plane device, records the requested `gx_render_plane_t`, opens the wrapper, and optionally clears the plane device to white. The device prototype `gs_plane_extract_device` overrides drawing procedures such as rectangle fill, monochrome/color copies, alpha copy, path fill/stroke, masks, parallelograms, triangles, tiled rectangles, RasterOp copies, typed images, and get-bits rectangle.

The main reduction mechanism is `reduce_drawing_color`. It attempts to transform a Ghostscript drawing color into an equivalent color for the selected plane. It handles pure colors, binary halftones, and colored halftones. It can skip operations that would only write plane-white before any marks have occurred, using `any_marks` as an optimization. It also accounts for RasterOp texture transparency, rejecting cases where plane-only reduction would be semantically unsafe.

For source pixmaps and tiles, the file defines `tiling_state_t` and helpers `begin_tiling`, `extract_partial_tile`, `next_tile`, and `end_tiling`. These allocate or reuse small local buffers, extract the requested plane with `bits_extract_plane`, and process large operands in subtiles when required.

Most drawing procedures reduce colors and forward to the plane device when safe, otherwise they fall back to Ghostscript defaults so the full target semantics are preserved. `plane_copy_color` has a direct fast path when the plane device is a compatible memory device. `plane_strip_copy_rop` reduces source/texture colors when possible, but punts to the default implementation for transparency-heavy RasterOps.

The image path wraps a target image enumerator with `plane_image_enum_t`, replaces color-map procedures so image colors are reduced as they are produced, and frees copied imager state on image end. The readback path supports planar single-plane retrieval and can expand a plane back into chunky pixels for default RasterOp use.

Filesystem relevance: none directly. This is raster-buffer infrastructure used by printer and banding devices, including files in this group.
