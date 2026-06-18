# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcmap.c

Core Ghostscript device color mapping implementation.

Key behavior:
- Defines GC descriptors for `gx_device_color`.
- Implements default separable/linear `encode_color` and `decode_color` using device component shifts, masks, and bit widths.
- Provides error and grayscale fallback encoders, including compatibility with old devices that only implement `map_rgb_color`.
- Defines default color-space-to-device-model conversions for DeviceGray, DeviceRGB, DeviceCMYK, and DeviceRGBK.
- Supplies default color-component-name lookup for Gray/RGB/CMYK/RGBK devices.
- Selects direct vs halftoned color-map procedure tables based on `gx_device_must_halftone`.
- Implements remapping for DeviceGray, DeviceRGB, and DeviceCMYK client colors, preserving original client-color values in the device color.
- Maps gray/RGB/CMYK/RGB-alpha/Separation/DeviceN fractions through device color-model procs, transfer maps, device polarity, encode_color, and halftone fallback.
- Implements transfer-map helpers: identity transfer, mapped transfer, identity-map initialization, and optional interpolating fraction map.
- Provides default device color-index mappings for 1-bit monochrome, grayscale, 8-bit gray, RGB, CMYK, and RGB-alpha compatibility.

Notable dependencies:
- `gxcspace.h`, `gxcmap.h`, `gxdcconv.h`, `gxcdevn.h`, transfer-map and halftone rendering infrastructure.

Research notes:
- The central pipeline is: color space fractions -> device color model components -> transfer/polarity adjustment -> direct color index or halftoned DeviceN color.
- DeviceN and Separation support use `gs_devicen_color_map` to place input components into device colorant order.
- Direct mapping falls back to halftoning if `encode_color` returns `gx_no_color_index`.
- CMYK remapping explicitly ignores alpha.
- The RGB-to-CMYK default path contains a suspicious fallback expression using `min(m, g)` when deriving `k`; this may be intentional legacy code but deserves caution if touched.
