# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsd.c

## Purpose
Implements Photoshop PSD raster export devices with RGB, CMYK, DeviceN, and spot-color support. Despite the `gdevpsd` prefix, this is a printer/raster output device, not the shared PostScript/PDF distiller layer.

## Main Structures And Devices
- `psd_device`: combines common device/printer state, DeviceN parameters, equivalent CMYK spot-color metadata, selected PSD process color model, and disabled-by-default ICC profile fields.
- `gs_psdrgb_device`: RGB PSD export device.
- `gs_psdcmyk_device`: CMYK/DeviceN PSD export device with spot separations.
- `psd_write_ctx`: per-page writer context for dimensions, channel counts, separation/channel mapping, and output file state.

## Key Behavior
- Defines device procedures for open, get/put parameters, print-page output, color mapping, component lookup, color encode/decode, and equivalent spot-color updates.
- Supports `DeviceGray`, `DeviceRGB`, `DeviceCMYK`, and `DeviceN` through `ProcessColorModel`.
- Uses DeviceN helpers for separation names, separation order, component lookup, and equivalent CMYK colors.
- Encodes multiple 8-bit components into `gx_color_index` according to active bits-per-component and component count.
- Writes PSD data directly:
  - `8BPS` signature and version,
  - channel count, dimensions, depth, and mode,
  - image resources for channel names,
  - display color metadata for spot channels,
  - resolution resource,
  - raw uncompressed planar image data.
- Converts Ghostscript interleaved printer rows into PSD channel planes; CMYK data is inverted because Photoshop stores channel values additively.
- ICC profile code exists behind `ENABLE_ICC_PROFILE`, but that macro is `0` in this file.

## Dependencies
Uses printer-device infrastructure, DeviceN and separation helpers, equivalent CMYK spot-color logic, color conversion helpers, and optional ICC types.

## Research Notes
`psd_write` checks `fwrite` with `< 0`, but `fwrite` reports write failure through a short item count rather than a negative value, so short writes are not robustly surfaced. The disabled ICC path also contains code that appears to use converted output before calling `lookup`; this is inactive with `ENABLE_ICC_PROFILE == 0`.
