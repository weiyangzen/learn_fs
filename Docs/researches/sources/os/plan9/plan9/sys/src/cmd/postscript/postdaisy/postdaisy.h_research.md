# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdaisy/postdaisy.h

Local definitions for the Diablo 1640 PostScript translator.

Contents:
- Defines a working resolution of `RES=240`, with Diablo horizontal/vertical scaling factors `HSCALE=2` and `VSCALE=5`.
- Defines default horizontal and vertical motion indexes:
  - `HMI = 12 * HSCALE`
  - `VMI = 8 * VSCALE`
- Defines default margins and page bounds in the 240-dpi coordinate system.
- Defines fixed tab array sizes `ROWS=400` and `COLUMNS=200`.
- Defines `Fontmap`, mapping user-facing aliases to PostScript font names.
- Provides `FONTMAP` initializer for Courier, Courier-Oblique, and Courier-Bold aliases.
- Declares `char *get_font()`.

Role:
- Supplies the printer geometry, font alias table, and tab table dimensions consumed by `postdaisy.c` and `Opostdaisy.c`.

Risks and quirks:
- Comments acknowledge that fixed tab arrays should ideally be allocated after HMI/VMI are known.
- The code using these constants confuses `ROWS` and `COLUMNS` in several loops, making the fixed dimensions part of a real bounds-risk surface.
