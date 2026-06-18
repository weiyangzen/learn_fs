# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcd8.c

## Purpose
Implements Ghostscript printer drivers for HP color DeskJet-style devices: `cdj670`, `cdj850`, `cdj890`, and `cdj1600`.

## Devices
- `gs_cdj670_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj850_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj890_device`: 600 dpi CMYK-capable path, default 32 bpp.
- `gs_cdj1600_device`: 300 dpi CMY/PCL-style path, default 24 bpp.

## Major Components
- Gamma lookup tables for 850-family and 890-family behavior.
- Device structs that extend printer devices with CMYK state, default depth, correction flags, quality, paper type, intensity count, scaling flags, printer type, compression mode, gamma values, black correction, and printer-command function pointers.
- Parameter handlers for quality, paper type, gamma, black correction, and bits per pixel.
- Print-page pipeline with buffer allocation, gamma/GCR preparation, raster-mode setup, scan-line processing, compression, and page termination.
- Floyd-Steinberg dithering for black and color planes, including 2-, 3-, and 4-intensity color output.
- HP PCL mode 9 compression for cdj850-style output and mode 3 compression for cdj1600-style output.

## Open/Configuration Behavior
- `hp_colour_open` chooses resolution and scaling based on printer type, quality, and media type.
- Margins are set for A4/letter DeskJet devices or fixed CDJ1600 margins.
- `cdj850_start_raster_mode` emits HP raster setup including page size, quality, media type, top offset, CMYK raster configuration, and compression.
- `cdj1600_start_raster_mode` enters PCL mode, sets resolution/page/media/quality/raster width/plane count, then starts raster graphics.

## Rendering Pipeline
- `cdj850_print_page` copies gamma tables, optionally recomputes gamma curves, computes black correction, allocates one large working buffer, initializes pointer slices, starts raster mode, sends scan lines, terminates the page, and frees memory.
- `send_scan_lines` skips blank lines, preserves plane buffers across compression, and dispatches nonblank rows to the device-specific output function.
- `cdj850_print_non_blank_lines` performs grey component replacement, dithers the black plane, emits black, rescales color planes as needed, dithers C/M/Y, and emits lower/upper color planes depending on intensity count.
- `cdj1600_print_non_blank_lines` copies color data to the color buffer, dithers color planes, and emits PCL mode 3 compressed planes.

## Color Processing
- `do_gcr` performs grey component replacement / undercolor handling and applies gamma lookup tables.
- `do_gamma` builds gamma-adjusted lookup tables.
- `do_black_correction` builds a correction table used during GCR.
- `rescale_byte_wise1x1`, `1x2`, `2x1`, and `2x2` adapt color-plane resolution relative to black-plane resolution.

## Color Mapping
- `gdev_cmyk_map_cmyk_color` packs CMYK-like values into the driver’s K,C,M,Y internal order.
- `gdev_cmyk_map_rgb_color` supports mono/gray mapping for CMYK devices.
- `gdev_cmyk_map_color_rgb` decodes packed CMYK values to RGB.
- `gdev_pcl_map_rgb_color` and `gdev_pcl_map_color_rgb` handle PCL-style gray/CMY/RGB packed depths from 1 to 32 bpp.
- `cdj_set_bpp` switches among mono, RGB/CMY, and CMYK modes and updates device color metadata/procs.

## Parameters
- `cdj850_get_params` reports `Quality`, `Papertype`, `MasterGamma`, individual gamma values, and `BlackCorrect`.
- `cdj850_put_params` validates and stores those parameters, then routes bits-per-pixel changes through `cdj_put_param_bpp` / `cdj_set_bpp`.
- Quality accepted by `put_params` is checked as 0..2 even though the enum uses `DRAFT = -1`; that mismatch is worth preserving/understanding before changing behavior.

## Memory Layout
- `calculate_memory_size` computes scan-line, plane, error, output, and total storage sizes.
- `init_data_structure` slices one allocation into alternating input buffers, error buffers, plane buffers, color buffers, upper/lower intensity buffers, and output compression storage.

## Notes
- The file is self-contained and old-style C, with `P1`..`P12` compatibility macros.
- Dithering intentionally random-seeds error buffers for high-bit-depth modes to avoid uniform first rows.
- There is a notable indexing concern in `gdev_cmyk_map_cmyk_color`: it assigns `yellow = cmyk[3]` and `black = cmyk[4]`, which is atypical for a four-element CMYK array and should be verified before relying on or modifying that mapper.
