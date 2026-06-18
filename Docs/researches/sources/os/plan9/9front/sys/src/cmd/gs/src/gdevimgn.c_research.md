# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevimgn.c

## Role
`gdevimgn.c` implements the Imagen ImPRESS printer device `imagen`.

## Device and Configuration
- Supports byte-stream quoting when `USE_BYTE_STREAM` is defined, including quote and EOF handling for Imagen hardware/spoolers.
- Uses `IMPRESSHEADER` from the environment, or a default document header string.
- Defaults to Canon CX-style 300 DPI maximum and computes imPress magnification from the requested resolution.
- Defines many ImPRESS opcodes such as page, bitmap, absolute positioning, magnification, endpage, and EOF.

## Lifecycle
- `imagen_prn_open` opens the Ghostscript printer output, writes an imPress document header, then closes the printer stream for later page output.
- `imagen_prn_close` reopens output in append mode, writes imPress EOF and optional byte-stream EOF, flushes, closes printer output, then closes the Ghostscript printer device.

## Print Path
- `imagen_print_page` reads page data one scanline at a time, organizing it into 32x32-bit imPress swatches.
- Allocates:
  - `in`: one raster line plus alignment slack.
  - `out`: one row of 32-line swatches.
  - `swatchMap`: flags indicating blank/nonblank swatches.
- For each 32-line band, it interleaves scanlines into swatch order, marks nonblank swatches, then emits only contiguous runs of nonblank swatches using absolute vertical/horizontal positioning and the `iBITMAP` command.
- Ends each page with `iENDPAGE`.

## Risks and Notes
- File output is explicit and multi-phase: document header on open, page bodies, document EOF on close.
- Uses environment variable `IMPRESSHEADER` to affect generated output.
- Returns `-1` on some allocation failure paths rather than a Ghostscript-specific error code.
