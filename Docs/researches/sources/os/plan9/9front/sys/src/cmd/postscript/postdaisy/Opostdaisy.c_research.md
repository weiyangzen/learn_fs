# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdaisy/Opostdaisy.c

`Opostdaisy.c` is an older copy of the Diablo 1640 to PostScript translator. It is almost identical to `postdaisy.c` but lacks the later Plan 9/nonprintable character adjustments.

Main behavior:
- Converts Diablo 1640 printer text/control streams into PostScript.
- Emits DSC header/prologue/setup, processes input files, emits trailer and accounting.
- Maintains printer-like state: horizontal/vertical position, margins, horizontal and vertical motion indexes, tab stops, line/page limits, reverse print mode, and shadow/bold font mode.
- Implements control characters for backspace, tabs, line feed, form feed, carriage return, and ESC sequences.
- Emits accumulated text strings to PostScript procedure `t`, minimizing stack entries by grouping runs at the same y/hmi state.
- Uses page redirection through `in_olist()` and `/dev/null`.

Differences from current `postdaisy.c`:
- Does not include `sys/types.h`.
- Does not define `isascii()` for Plan 9.
- Has a local `int interrupt();` declaration in `init_signals()`.
- In `text()`, default characters are only passed to `oput()` if `isascii(ch) && isprint(ch)`.
- In `oput()`, output directly writes the byte after escaping `\`, `(`, and `)`, with no octal fallback for nonprintable bytes.

Limitations:
- Graphics mode ESC commands are fatal/unimplemented.
- Tabs are fixed-size arrays and can be indexed from position-derived values without strong bounds checks.
- Comments warn that page/document font comments may be inaccurate.
- Reverse printing and some device behaviors were not fully tested.

Filesystem relevance: none direct; it is an archived/old variant of a PostScript text translator.
