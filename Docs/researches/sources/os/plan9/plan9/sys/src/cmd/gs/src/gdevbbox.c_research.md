# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.c

Ghostscript bounding-box accumulator device. It can run as a standalone `bbox` device that prints page bounding boxes at page output, or as a forwarding wrapper around another target device while tracking the painted extent.

Key behavior:
- Defines `gs_bbox_device` as an 8-bit gray, high-resolution pseudo-device sized near the fixed-point coordinate limit.
- Maintains a `gs_fixed_rect bbox`, mapped black/white/transparent colors, and pluggable box procedures for init/get/add/in-rect.
- `gx_device_bbox_init` clones the bbox prototype, optionally attaches a target, fills forwarding procedures, and redirects color/page-device operations to the target.
- `bbox_open_device` initializes the box and optionally opens the target; `bbox_close_device` optionally closes the target and frees compositor-created wrappers.
- `bbox_output_page` prints `%%BoundingBox` and `%%HiResBoundingBox` for standalone use, then forwards page output.
- Low-level drawing hooks update the accumulated box for rectangles, mono/color/alpha copies, strip tiles, ROP copies, trapezoids, parallelograms, triangles, and thin lines.
- High-level path hooks try to use path/stroke extents directly when unclipped, but fall back through default rendering with `target = NULL` when clipping means the exact bbox must be derived from generated pieces.
- Image handling wraps the target image enumerator, forwards image data, computes transformed source-row bounds, and handles clipping by drawing two triangles through a clip device.
- `bbox_create_compositor` creates a target compositor and wraps it in another bbox device that forwards bbox updates into the original accumulator.
- `bbox_text_begin` uses default text handling and adjusts the text enumerator imaging device when forwarding.

Notable dependencies:
- Core Ghostscript device and forwarding infrastructure: `gxdevice.h`, `gsdevice.h`, `gdevbbox.h`.
- Drawing/color/path/image internals: `gxdcolor.h`, `gxiparam.h`, `gxistate.h`, `gxpaint.h`, `gxpath.h`, `gxcpath.h`.

Research notes:
- This file is a central utility wrapper, not a printer/file-format backend like many neighboring `gdev*` files.
- White can be treated as transparent or opaque through `WhiteIsOpaque`; page-sized erases reinitialize the bbox unless white is opaque.
- The file exposes `PageBoundingBox` through device parameters and accepts a written bbox back through `put_params`.
- There is a likely typo in `bbox_draw_thin_line`: the forwarded target call passes `(fx0, fy0, fx1, fy0, ...)`, using `fy0` for both endpoints instead of `fy1`. Bounding-box accumulation still uses `fy1`, so forwarding and measured output can diverge.
- The image-row bbox logic advances by the submitted `height`, relying on the target enumerator's row consumption behavior. If partial consumption differs from `height`, this may over-accumulate, though overestimation is safer than underestimation for bbox use.
