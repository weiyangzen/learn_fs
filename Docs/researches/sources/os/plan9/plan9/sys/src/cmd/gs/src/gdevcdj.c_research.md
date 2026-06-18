# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcdj.c

Large Ghostscript printer-driver collection for HP/Canon color printers. It defines multiple device descriptors and a shared print pipeline for HP DeskJet/PaintJet/DesignJet/LaserJet variants, Epson ESC/P output, and Canon BJC raster-mode printers.

Key responsibilities:
- Defines Ghostscript devices including `cdjmono`, `cdeskjet`, `cdjcolor`, `cdj500`, `cdj550`, optional `cdj550cmyk`, `declj250`, `dnj650c`, `lj4dith`, `pj`, `pjxl`, `pjxl300`, `escp`, `escpc`, `bjc600`, and `bjc800`.
- Implements open routines that choose paper-size-specific hardware margins and initialize printer color depth/component metadata.
- Implements device parameter get/put paths for DeskJet shingling/depletion/black correction, PaintJet XL print quality/render type, BJC media/manual feed/quality/dithering/process color model/media weight/version metadata, and bits-per-pixel changes.
- Provides `hp_colour_print_page`, the central rasterization/output loop for all HP-like, ESC/P, and BJC-like devices.
- Converts Ghostscript rendered scanlines into printer color planes, handles blank-line skipping, shingled/head-row behavior, and emits device-specific PCL, HP-RTL, ESC/P, or Canon raster commands.
- Implements compression helpers: HP PaintJet mode 1 run-length compression, BJC PackBits-style compression, and selection between PCL mode 2 and mode 3 where supported.
- Implements RGB/CMYK color mapping and reverse mapping for PCL and BJC/CMYK-capable devices.
- Implements scanline expansion between packed 3/8/16/24-bit representations and 24/32-bit CMY/CMYK working formats.
- Implements Floyd-Steinberg dithering macros for gray/RGB/CMY/CMYK and a specialized BJC CMYK error-diffusion algorithm.

Important behavior:
- `hp_colour_open` mutates margins based on printer type and paper size, then calls `gdev_prn_open`.
- CMYK-capable devices use `cprn_device->cmyk` as a tri-state: positive for CMYK printing, negative for CMYK-capable but RGB/PCL mapping, zero for non-CMYK.
- `cdj_set_bpp` can change device color procedures and close an already-open device when color model/depth changes.
- DeskJet 500/550 use PCL mode 9 compression; DesignJet uses HPGL/2 plus HP-RTL and mode 1; PaintJet XL can select mode 2 or mode 3 per row; BJC uses Canon raster commands and PackBits-style compression.
- For some printer modes, rendered RGB/CMY data is inverted or decomposed into K/CMY planes before output.
- ESC/P output buffers head-height groups, transposes raster data into vertical nozzle order, optimizes horizontal skips, and flushes in bands.
- BJC page initialization emits Canon command sequences for page mode, margins, compression, paper loading, printing method, resolution, raster transfer, vertical skips, and page finish.
- `bjc_fscmyk` initializes and maintains a private CMYK error buffer, scans alternate directions, generates K-only output for gray cases, and clips CMY error in K-only regions.

Dependencies:
- Ghostscript printer/device APIs: `gdevprn.h`, `gdevpcl.h`, `gsparam.h`, `gsstate.h`, color value helpers, and Canon BJC constants from `gdevbjc.h`.
- Uses PCL compression helpers from other Ghostscript modules: `gdev_pcl_mode2compress`, `gdev_pcl_mode3compress`, `gdev_pcl_mode9compress`.
- Relies on Ghostscript memory allocation, scanline copying, device params, and device color procedure conventions.

Notable risks:
- The file is explicitly marked as hard to maintain and no longer accepting changes; its logic is dense, macro-heavy, and tightly coupled across printer families.
- Many paths share global/static ESC/P state (`ep_storage`, `ep_raster_buf`, `ep_print_buf`, `img_rows`), making reentrancy and concurrent use unsafe.
- Several calculations depend on exact buffer sizing across packed/expanded depths; mistakes can corrupt adjacent working regions.
- BJC and ESC/P code uses many empirically derived limits and hard-coded hardware command bytes.
- `cdj_put_param_bpp` temporarily mutates `pdev->color_info.depth` to pass Ghostscript parameter validation, then resets it, which is fragile.
- `bg_and_ucr` macro appears suspect: the black component calculation uses `kv = (yv > k ? k : y)`, mixing original variable names rather than the temporary `yv`.
- `gdev_cmyk_map_color_cmyk` has a parameter name `prgb[3]` but may write four CMYK values in the default path.
- Several functions return generic `0` or `rangecheck` and do not preserve detailed printer/protocol failure context.
