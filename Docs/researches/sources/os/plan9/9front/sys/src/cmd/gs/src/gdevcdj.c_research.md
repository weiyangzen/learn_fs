# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcdj.c

Ghostscript HP/Canon color printer backend containing many device definitions in one legacy file: DeskJet/PaintJet/DesignJet/LaserJet dithering, Epson ESC/P, and Canon BJC variants. It defines device structs for HP-style RGB/CMY devices and BJC CMYK-capable devices, device procedure tables, exported `gs_*_device` descriptors, open/parameter/print routines, raster packing, PCL/ESC/P/BJC command output, compression, and color mapping.

Key behavior:
- `hp_colour_open` selects margins by printer type and paper size, initializes color depth via `cdj_set_bpp`, and opens the printer device.
- `cdj_get_params`, `cdj_put_params`, `pjxl_*`, `pj_put_params`, and `bjc_*_params` expose device options such as `BitsPerPixel`, `BlackCorrect`, `Shingling`, `Depletion`, `PrintQuality`, `RenderType`, `ProcessColorModel`, media type, media weight, manual feed, dithering type, and print colors.
- `hp_colour_print_page` is the central raster pipeline. It allocates working buffers, copies rendered scanlines, handles blank-line skipping, expands packed pixel formats, dithers RGB/CMYK data, separates planes, chooses printer-specific compression, writes printer control streams, and ejects/finalizes pages.
- Compression support includes local PCL mode 1, imported/used PCL mode 2/3/9 paths, BJC PackBits-like compression, and ESC/P transposition buffers.
- Color functions map RGB/CMY/CMYK across 1/3/8/16/24/32-bit modes, with optional black correction and CMYK-specific encode/decode behavior.

Notable dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gdevpcl.h`, `gsparam.h`, `gsstate.h`.
- Color/luminance helpers: `gxlum.h`.
- Canon BJC constants/options from `gdevbjc.h`.

Research notes:
- This is vendor/legacy Ghostscript printer output code, not filesystem logic, but it is part of the in-scope 9front Ghostscript source tree.
- The file itself warns that no further changes were accepted historically and that the drivers were planned for rewrite; the implementation reflects that: many compile-time flags, global ESC/P buffers, macro-heavy dithering, and printer-specific command knowledge are tightly coupled.
- Memory ownership in `hp_colour_print_page` is manual; allocation failure returns VM errors, but there are paths where one allocation may have succeeded before another fails.
- `bjc_fscmyk` embeds an adapted Floyd-Steinberg CMYK algorithm with persistent error buffer layout packed into caller-provided storage.
