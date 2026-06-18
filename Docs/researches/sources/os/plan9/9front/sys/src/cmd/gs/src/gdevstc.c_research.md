# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc.c

Main Ghostscript Epson Stylus Color printer driver. It manages device parameters, color mapping, scanline conversion, dithering dispatch, ESC/P2 raster emission, weaving, and compression.

Key behavior:
- Defines the public `stcolor` device, defaulting to CMYK direct mode at the DPI and margins declared in `gdevstc.h`.
- Registers built-in dither algorithms `gscmyk` and `hscmyk`, plus external algorithms from `STC_MODI`.
- Exposes Ghostscript device procedures for open, close, page printing, parameter get/put, and color mapping.
- Computes ESC/P2 resolution units, line spacing, band height, page length, margins, initialization sequence, release sequence, color selection, and unidirectional/microweave settings.
- Implements the main print loop: allocate scanline/band/dither buffers, read rendered scanlines, skip white lines, convert Ghostscript pixels into algorithm input, invoke the selected dither function, split color bits into printer planes, and emit bands.
- Supports plain output, ESC/P2 RLE output, and delta-row compression.
- Supports single-pass bands, software/hardware weave, and delta-row-specific output.
- Builds internal code and transfer lookup arrays from PostScript parameters such as `Ccoding`, `Ctransfer`, `Kcoding`, and `Ktransfer`.
- Implements color adjustment through 3-, 9-, or 16-element `ColorAdjustMatrix`.
- Handles DeviceGray, DeviceRGB, DeviceCMYK, and special CMYK10 packed color mappings.
- Provides reverse color mapping for gray/RGB/CMYK/CMYK10 where needed.
- Publishes parameters including `Version`, `BitsPerComponent`, `Algorithms`, `OutputCode`, `Model`, weave flags, ESC/P2 geometry fields, init/release strings, dither name, color matrix, and transfer/coding arrays.
- Validates and applies parameters for model, dithering, bit depth, output coding, weave mode, flags, ESC/P2 settings, color adjustment, and transfer arrays.
- Closes/reopens the device when parameter changes require recalculating buffers or color state.
- Includes internal `gscmyk` direct 1-bit CMYK unpacking and `hscmyk` CMYK10 error-diffusion algorithms.

Notable dependencies:
- Shared Stylus Color declarations from `gdevstc.h`.
- External dither implementations in `gdevstc1.c`, `gdevstc2.c`, `gdevstc3.c`, and `gdevstc4.c`.
- Ghostscript printer, parameter, and color APIs through `gdevprn.h`, `gsparam.h`, and `gsstate.h`.
- Optional POSIX signal handling under `STC_SIGNAL`.

Research notes:
- This is the central file of the Stylus Color driver family.
- The code is parameter-heavy and uses persistent device state; correctness depends on careful open/close behavior when changing parameters.
- Memory management is manual and complicated because arrays can be shared between color components.
- A likely typo/bug exists in `stc_freedata`: it references `sd->stc.alg_item` although the function receives only `stc_t *stc`; this would depend on an out-of-scope `sd`.
- The file is printer rendering/output code, not filesystem code.
