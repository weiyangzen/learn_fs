# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdflt.c

Provides Ghostscript’s default device procedure implementation and color-model inference/fallback logic.

The file derives default `encode_color` and `decode_color` procedures from device color information, old-style mapping procs, polarity, and separable/linear flags. It can recognize DeviceRGB-like and DeviceCMYK-like mappings by probing sample colors, includes gray and CMYK fallback decoders, and has a special 1-bit CMYK decoder.

`set_linear_color_bits_mask_shift` initializes per-component bit fields for separable linear devices. `check_device_separable` probes `encode_color` with zero and max component values to infer non-overlapping component masks, shifts, and bit widths.

`gx_device_fill_in_procs` fills missing device procs with defaults: open/close/output, matrix, copy/fill/path/stroke, trapezoid/parallelogram/triangle/thin-line from `gdevddrw.c`, image begin/data/end compatibility wrappers, get-bits routines, compositors, pattern management, color-space inclusion, linear-color fills, and spot-equivalent-color update. It also installs default color mapping and component-index procedures for Gray, RGB, CMYK, or error cases.

Other defaults include initial matrices for inverted/upright Y, sync/output/close stubs, clipping boxes, compositor creation, copydevice validation, page install/begin/end hooks, and no-op pattern/color-space handlers.

Risks: this file is central to device behavior. Incorrect inferred polarity or separability affects overprint, halftoning, shading, and color encoding. Many defaults are intentionally best-effort compatibility paths for older devices and may be approximate.
