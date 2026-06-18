# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsd.c

## Purpose
Implements Photoshop PSD raster export devices with DeviceN and spot-color support. Despite the similar filename prefix, this is a printer/raster output device rather than part of the PostScript vector writer.

## Main Structures And Devices
- `psd_device`: combines `gx_device_common`, `gx_prn_device_common`, DeviceN parameters, equivalent CMYK spot colors, selected color model, and optional ICC profile handles.
- `gs_psdrgb_device`: RGB PSD export device.
- `gs_psdcmyk_device`: CMYK/DeviceN PSD export device with spot color support.
- `psd_write_ctx`: per-page PSD writer context with dimensions, channel maps, and output channel metadata.

## Key Behavior
- Defines device procedures for open, get/put params, print page, color mapping, color component lookup, color encode/decode, and equivalent spot color updates.
- Supports process color models:
  - `DeviceGray`,
  - `DeviceRGB`,
  - `DeviceCMYK`,
  - `DeviceN`.
- Uses DeviceN helpers to manage separation names/order and spot-color equivalents.
- Encodes component values into `gx_color_index` using the active bits per component.
- Writes PSD structures directly:
  - `8BPS` file header,
  - channel count, dimensions, depth, mode,
  - image resources for channel names,
  - spot channel display colors,
  - image resolution,
  - raw uncompressed planar image data.
- Maps Ghostscript interleaved page buffer data into PSD channel planes, inverting CMYK values as Photoshop expects additive component values.
- ICC profile support is present behind `ENABLE_ICC_PROFILE`, but disabled in this build.

## Dependencies
Uses printer device infrastructure, DeviceN helpers, equivalent CMYK spot-color logic, color conversion helpers, and optional ICC types.

## Research Notes
The implementation is focused on channel ordering and separation preservation. It writes uncompressed PSD image data and includes explicit Photoshop resource blocks for spot channel metadata.
