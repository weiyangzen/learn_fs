# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdflt.c

Ghostscript default device implementation. It fills missing device procedure slots, infers color encoding/decoding behavior, determines separable color layouts, and supplies no-op/default implementations for common device lifecycle and page operations.

Key behavior:
- `get_encode_color` derives an encoding procedure from explicit `encode_color`, legacy RGB/CMYK mapping procedures, monochrome defaults, or separable-linear color info.
- `is_like_DeviceRGB` and `is_like_DeviceCMYK` probe color mapping procedures with sample values to identify compatible standard color models.
- Default decode functions handle additive/subtractive one-component devices, separable devices, 1-bit CMYK, and approximate CMYK decode through RGB when necessary.
- `set_linear_color_bits_mask_shift` and `check_device_separable` populate component shift/mask/bit metadata for separable packed color indices.
- `gx_device_fill_in_procs` installs default procedure pointers for lifecycle, raster operations, paths, trapezoids, images, color mapping, compositor creation, clipping, patterns, shading, and spot equivalent colors.
- Default lifecycle/page functions mostly no-op or delegate: open initializes separability, output syncs then finishes page, close returns success.
- Default matrix functions provide inverted-Y and upright-Y device coordinate transforms.
- Default compositor, clipping-box, xfont, alpha-bit, pattern, and page callbacks provide baseline behavior.

Notable dependencies:
- Core Ghostscript device/color/compositor APIs: `gxdevice.h`, `gxcomp.h`, `gsropt.h`.

Research notes:
- This is central compatibility glue for old and new Ghostscript device APIs.
- Several defaults are intentionally conservative or approximate, especially CMYK decode through RGB and automatic separability probing.
- `gx_device_fill_in_procs` forcibly replaces obsolete `image_data` and `end_image` hooks with current wrappers and can warn in debug builds.
- The comments note known limitations: default initial matrices have wrong translation assumptions for devices with arbitrary initial matrices.
