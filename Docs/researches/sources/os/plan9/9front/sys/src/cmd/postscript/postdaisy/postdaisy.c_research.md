# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/postdaisy.c

`postdaisy.c` translates Diablo 1640 printer files to PostScript using a stateful emulation of Diablo text output.

Main flow:
- `main()` follows the common translator pattern: signals, header, options, setup, input arguments, trailer, accounting.
- `header()` emits DSC comments and copies `POSTDAISY`, optionally adding `ROUNDPAGE`.
- `options()` handles aspect ratio, copies, font, hmi/vmi, lines per page, forms per page, page list, orientation, CR/LF mode, point size, offsets, accounting, copy-through files, encoding, prologue, pass-through PostScript, requests, debug, and ignore-fatal.
- `text()` processes each byte and dispatches control characters and escape sequences.

Printer emulation:
- Coordinates use `RES=240`, with `HSCALE=2` and `VSCALE=5` from the header.
- `hmi`/`vmi` represent character and line spacing.
- Margins and tab stops are mutable via ESC sequences.
- `advance=-1` supports backward print mode.
- `shadowprint` switches to Courier-Bold until carriage return or explicit disable.
- Auto underscore uses Courier-Oblique.
- `markedpage` suppresses trailing blank page output.

Output strategy:
- `startline()`, `endstring()`, `endline()`, and `oput()` batch strings and positions for PostScript procedure `t`.
- Special PostScript string characters are escaped.
- Unlike `Opostdaisy.c`, current `oput()` emits octal escapes for nonprintable/non-ASCII bytes instead of dropping them before output.

Limitations and risks:
- Diablo graphics mode commands are fatal/unimplemented.
- `cleartabs()` loops appear swapped relative to array sizes (`ROWS` used for `htabstops`, `COLUMNS` for `vtabstops`), matching legacy code but potentially unsafe.
- Several tab/margin ESC operations index fixed arrays with position-derived values and no bounds checks.
- Document comments may be wrong when font changes occur through escape sequences.

Filesystem relevance: none direct; this is userland printer conversion code.
