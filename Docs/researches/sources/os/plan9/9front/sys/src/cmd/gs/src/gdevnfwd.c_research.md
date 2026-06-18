# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevnfwd.c

## Role

Generic null and forwarding device implementation for Ghostscript.

## Forwarding Device Responsibilities

- `gx_device_set_target` assigns forwarding targets with reference-count handling.
- `gx_device_forward_fill_in_procs` fills forwarding procedure slots for most device operations while leaving core low-level drawing/open/close choices to the caller.
- `gx_device_forward_color_procs` explicitly forwards color mapping and encoding/decoding operations.
- Dozens of `gx_forward_*` procedures delegate device operations to the target when present, or use defaults/errors when absent.

## Forwarded Areas

The file forwards or wraps:

- Initial matrix, sync/output page, get/put params.
- RGB/CMYK/RGBA color mapping and encode/decode.
- Xfont lookup device and procs.
- Get-bits, get-band, clipping box, hardware params.
- Raster operations, tile operations, mask/path/trapezoid/parallelogram/triangle fills.
- Images and typed images.
- Text begin.
- Color-space mapping callbacks and component-index lookup.
- Pattern management and linear-color fill helpers.
- Spot equivalent color updates.

## Color Mapping Detail

`gx_forward_get_color_mapping_procs` returns wrapper procs rather than the target’s raw mapping-proc table, because target mapping procs expect the target device pointer. The wrappers call the target with the correct device pointer or fall back to defaults.

## Null Devices

Exports:

- `gs_null_device`, named `null`, non-page device with upright initial matrix and zero size.
- `gs_nullpage_device`, named `nullpage`, page device with nominal 72x72 dimensions.

Null drawing operations return success without output. `null_put_params` prevents non-page null devices from acquiring real dimensions.

## Risks and Edge Cases

- Some forwarding operations return fatal/rangecheck errors when no target exists, while others fall back to defaults; caller expectations vary by operation.
- `gx_forward_copy_alpha` delegates to `copy_mono` with alpha-like arguments, reflecting older procedure compatibility assumptions.
- Reference-count finalization is described as a hack in the source comment.
