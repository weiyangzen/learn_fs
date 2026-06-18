# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevnfwd.c

Null-device and forwarding-device implementation.

- Provides target management for `gx_device_forward`, including reference-count assignment and finalization that decrements the target.
- `gx_device_forward_fill_in_procs` installs forwarding defaults for most higher-level device procedures while leaving open/close and low-level drawing operations to concrete devices.
- `gx_device_forward_color_procs` makes a forwarding device delegate color mapping and encode/decode to its target.
- Implements many `gx_forward_*` wrappers for close, matrix, sync, output page, color mapping, drawing, path fills/strokes, images, get-bits, text, hardware params, patterns, and color-space hooks.
- Fallback behavior varies: some wrappers call Ghostscript defaults when no target exists, while low-level mandatory operations may return fatal/rangecheck errors.
- Color mapping wrappers return forwarding color-map procs so the target device pointer is used correctly inside target mapping functions.
- `gx_forward_decode_color` clears component values if no target exists.
- Defines `gs_null_device` and `gs_nullpage_device`; both discard rendering operations, with `nullpage` behaving as a page device.
- Null procs return success for fills, copies, paths, trapezoids, triangles, thin lines, and strip-copy ROP; `null_put_params` prevents non-page null devices from keeping a reset size.
- Risk notes: `gx_forward_copy_alpha` delegates to `copy_mono` with alpha parameters, reflecting older Ghostscript proc compatibility assumptions; forwarding devices rely on target proc tables being correctly initialized.
