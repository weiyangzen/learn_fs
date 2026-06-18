# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevphex.c

Ghostscript printer driver for Epson Stylus Color Photo / Photo EX / Photo 700 class printers using ESC/P Raster.

Key behavior:
- Defines the `photoex` device with CMYK internal pixels, default `720x720` dpi, margins, and extra options for depletion, shingling, render method, splash, leakage, black inhibition, light ink levels, and dot size.
- Supports only `360x360`, `720x720`, and `1440x720` output; other resolutions return `rangecheck`.
- Implements RGB-to-CMYK mapping with hardcoded ink transfer curve, black extraction, hue-angle color compensation table, and empirical constants.
- Implements reverse device-color-to-RGB mapping for Ghostscript color queries.
- Handles device parameters: `Depletion`, `Shingling`, `Render`, `Splash`, `Leakage`, `Binhibit`, and `DotSize`.
- `photoex_print_page` validates width/resolution limits, allocates a large render context, initializes printer state with ESC/P commands, selects units, page length, margins, ink dot size, microweave/unidirectional settings, renders the page, ejects, resets, and frees memory.
- `RenderPage` drives the print pipeline: schedule nozzle lines, render/halftone needed scanlines, compute active byte ranges per color, move the print head, select ink, send ESC/P raster headers, RLE-compress each nozzle row, and write data.
- `RenderLine` avoids expensive halftoning for long runs of blank lines while respecting halftoner restart thresholds.
- The line scheduler handles leading, middle, and trailing page regions; it supports 720 dpi microweave and 1440 dpi two-phase horizontal weaving through precomputed start tables and band sizes.
- `PackLine` converts halftoned byte-per-pixel results into 1-bit packed raw device lines and records first/last active bytes.
- `RleCompress` and `RleFlush` implement ESC/P Raster run-length encoding for empty, repeated, and literal byte runs.
- ESC/P command helpers emit reset, margins, page length, graphics mode, unit, unidirectional mode, microweave, ink amount, vertical/horizontal movement, ink color selection, raster data header, and raw strings.
- Halftoning is abstracted through a function table with three methods: Floyd-Steinberg error diffusion, ordered clustered dither, and experimental Bendor error diffusion.
- `HalftoneLine` renders black first, optionally uses black output to inhibit color inks, handles light cyan/light magenta mid-level inks, and packs normal and 1440-phase raw lines for six device inks.
- Floyd-Steinberg uses a one-line error buffer and the classic 7/16, 3/16, 5/16, 1/16 diffusion pattern.
- Ordered dither uses a 16x16 threshold matrix.
- Bendor error diffusion uses two error lines, optional splash compensation, and intended leakage behavior.

Research notes:
- The top-of-file comments are extensive and document printer protocol assumptions, limitations, scheduling/weaving theory, color transformation, halftoning, compression, and known missing features.
- Shingling and depletion options exist structurally but are marked not implemented.
- The driver is printer/protocol logic, not filesystem code.
