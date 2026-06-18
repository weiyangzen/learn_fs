# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevp14.h

## Purpose

`gdevp14.h` declares the public and shared internal types for Ghostscript's PDF 1.4 transparency rendering device implemented in `gdevp14.c`.

## Contents

It defines `pdf14_default_colorspace_t` with `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`, then forward-declares `pdf14_buf` and `pdf14_ctx`.

`struct pdf14_buf_s` is the buffer-stack node used by transparency groups and masks. It stores the saved stack link, isolation/knockout flags, alpha/shape/blend mode, optional group-alpha and shape-plane presence, device rectangle, planar storage layout (`rowstride`, `planestride`, `n_chan`, `n_planes`, `data`), optional mask transfer function, and a bounding box of affected pixels.

`struct pdf14_ctx_s` owns the transparency stack, mask buffer, allocator, page rectangle, additive/subtractive polarity flag, and channel count.

`pdf14_device` extends `gx_device_forward_common` with a `pdf14_ctx`, current opacity/shape/combined alpha/blend mode, saved color-map callback, and saved clist color info.

The header exports `gs_pdf14_device_push` for installing a PDF 1.4 compositor device around a target and `send_pdf14trans` for sending PDF 1.4 compositor operations.

## Dependencies and Integration

The header assumes Ghostscript core types such as `gx_device`, `gs_imager_state`, `gs_pdf14trans_params_t`, `gx_color_map_procs`, `gx_device_color_info`, `gs_int_rect`, and `gs_blend_mode_t` are already visible through including contexts. It is tightly coupled to `gdevp14.c` and consumers that need to push or communicate with the PDF 1.4 transparency compositor.

## Filesystem Relevance

No filesystem logic is present. The file is device/compositor API surface only.

## Risks and Notes

The planar buffer layout is documented here and must remain consistent with all pointer arithmetic in `gdevp14.c`. `PDF14_MAX_PLANES` is private to the C file, so callers do not get a compile-time guard from this header.
