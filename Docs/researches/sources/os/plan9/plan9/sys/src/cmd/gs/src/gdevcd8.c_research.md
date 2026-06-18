# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcd8.c

Large Ghostscript HP Color DeskJet driver for `cdj670`, `cdj850`, `cdj890`, and `cdj1600` devices. It handles printer-specific setup, color calibration, CMYK/CMY mapping, gray component replacement, Floyd-Steinberg dithering, resolution scaling, and PCL raster compression.

Key behavior:
- Defines calibration/config data:
  - `hp850_cmyk_init` raster configuration bytes.
  - Gamma/calibration tables for HP 850-style and 890-style behavior.
  - Black-correction lookup generation.
- Defines `gx_device_cdj850`, which extends printer state with CMYK capability, default depth, quality, paper type, intensity count, scaling flags, printer type, compression mode, gamma values, black correction, and function pointers for printer-specific start/print/terminate routines.
- Exports devices:
  - `gs_cdj670_device`: 600 DPI CMYK-style device.
  - `gs_cdj850_device`: 600 DPI CMYK-style device.
  - `gs_cdj890_device`: 600 DPI CMYK-style device.
  - `gs_cdj1600_device`: 300 DPI CMY/PCL-style device.
- `hp_colour_open` sets color parameters if needed, chooses effective resolution/scaling/intensity based on printer type, paper type, and quality, sets paper margins, then opens the printer.
- `cdj850_get_params`/`cdj850_put_params` expose `Quality`, `Papertype`, `MasterGamma`, per-channel gamma values, `BlackCorrect`, and `BitsPerPixel`.
- `cdj850_print_page` copies gamma tables locally, optionally applies gamma transforms, computes black correction, calculates a single large work buffer, initializes internal pointer slices, starts raster mode, sends scanlines, terminates the page, and frees storage.
- `send_scan_lines` skips blank lines, handles y-scaling and two-pass color timing, and dispatches nonblank rows to the device-specific line printer.
- `cdj850_print_non_blank_lines` performs gray component replacement, black-plane dithering, mode-9 compressed black output, color-plane rescaling, color dithering, and compressed C/M/Y plane output.
- `cdj1600_print_non_blank_lines` copies 24-bit color input into the color buffer, dithers CMY planes, and outputs mode-3 compressed planes.
- `do_gcr` performs gray component replacement and applies C/M/Y/K calibration lookup tables.
- `FSDlinebw`, `FSDlinec2`, `FSDlinec3`, and `FSDlinec4` implement bidirectional Floyd-Steinberg dithering for black and color planes with two, three, or four intensity levels.
- Rescale functions average color data for 1x/2x in X and Y so black and color planes can run at different resolutions.
- `cdj_set_bpp` and `cdj_put_param_bpp` manage accepted bit depths, process color model changes, color component counts, mapping procedure changes, and device close/reopen needs.
- PCL setup differs between the DeskJet 850-style path and the `cdj1600` path, including PJL/PCL entry for `cdj1600`.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Parameter API: `gsparam.h`.
- Luminance helpers: `gxlum.h`.
- PCL compression helpers: `gdev_pcl_mode9compress` and `gdev_pcl_mode3compress`.

Research notes:
- This is printer/raster code, not filesystem logic, but it is in the included Plan 9 Ghostscript source tree.
- The driver keeps extensive legacy comments about printer model support, quality/paper switches, gamma usage, and performance costs of 600 DPI color rendering.
- Work memory is manually partitioned from a single allocation; correctness depends on `calculate_memory_size` matching every pointer slice in `init_data_structure`.
- The code uses the `scan` variable both for bidirectional dithering direction and alternating compression buffers; comments call out this overload explicitly.
- `cdj850_get_params` writes `MasterGamma` from `cdj850->gammavalc` rather than `cdj850->mastergamma`, which looks like a parameter reporting bug.
- `cdj850_put_params` documents `Quality` as `-1,0,1`, but validates it with minimum `0`, so `DRAFT = -1` cannot be set through this path despite comments.
- `gdev_cmyk_map_cmyk_color` assigns `yellow = cmyk[3]` and `black = cmyk[4]`, which is suspicious for a four-component CMYK array and may be an out-of-bounds/indexing bug unless this old Ghostscript calling convention supplies a different layout.
