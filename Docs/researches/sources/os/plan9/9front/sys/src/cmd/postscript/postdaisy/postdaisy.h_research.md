# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.h

`postdaisy.h` provides device geometry and font alias definitions for the Diablo 1640 translator.

Key definitions:
- `RES=240` establishes internal coordinate resolution.
- `HSCALE=2` and `VSCALE=5` convert Diablo horizontal/vertical units to the internal resolution.
- Default spacing: `HMI=(12 * HSCALE)`, `VMI=(8 * VSCALE)`.
- Default margins are `LEFTMARGIN=0`, `RIGHTMARGIN=3168`, `TOPMARGIN=0`, `BOTTOMMARGIN=2640`.
- Tab arrays are fixed at `ROWS=400` and `COLUMNS=200`.
- `Fontmap` and `FONTMAP` map aliases such as `R`, `I`, `B`, `CO`, `CI`, `CB`, `CW`, and lowercase Courier names to Courier PostScript fonts.
- Declares non-integer function `get_font()`.

It is a small configuration/typing header used only by the daisy translator.
