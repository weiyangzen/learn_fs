# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbit.c

## Purpose
Implements “plain bits” printer devices used to measure rendering/output time by dumping raw rendered raster data.

## Devices
- `gs_bit_device`: monochrome `bit`
- `gs_bitrgb_device`: RGB `bitrgb`
- `gs_bitcmyk_device`: CMYK `bitcmyk`

## Main Behavior
- Uses printer-device infrastructure but does not implement drawing operations directly; rendering happens through the standard printer/memory path.
- `bit_print_page` writes each scan line’s raw bytes to the output file, unless the output filename is `nul`, in which case it skips writes after rendering.
- Supports variable bits per component through parameters like `GrayValues`, `RedValues`, `GreenValues`, and `BlueValues`.
- Supports `ForceMono`, which can force RGB/CMYK devices to behave as 1-component monochrome devices while preserving the real component count internally.

## Color Mapping
- `bit_mono_map_color` maps gray to packed gray/mono output, with inverted 1-bit mono semantics.
- `bit_map_color_rgb` decodes gray, RGB, or CMYK packed color indices back to RGB.
- `bit_map_cmyk_color` packs CMYK component bits into a color index and avoids `gx_no_color_index`.

## Parameters
- `bit_get_params` temporarily restores the real component count before delegating to printer params and exposing `CRDDefault` plus `ForceMono`.
- `bit_put_params` validates component value counts, updates depth/dither info, applies `ForceMono`, closes the device when color layout changes, and resets CMYK mapping procs.

## Dependencies
Uses `gdevprn.h`, `gsparam.h`, CRD helpers, luminance helpers, and device color-rendering defaults.
