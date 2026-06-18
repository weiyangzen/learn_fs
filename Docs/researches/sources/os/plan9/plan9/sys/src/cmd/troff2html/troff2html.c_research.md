# File Research: sources/os/plan9/plan9/sys/src/cmd/troff2html/troff2html.c

Read fully: 795 lines, 14275 bytes. SHA-256 prefix: `620cad355d16e3a0`.

This command converts troff device output, especially man-page output prepared for HTML, into HTML. It parses emitted typesetter directives, tracks font and layout state, buffers attributed characters, and flushes them with properly nested tags.

Important behavior:
- `main()` handles `-d` and `-t`, initializes character mappings, emits header, processes files/stdin, then emits trailer.
- `emit()`, `emitstr()`, and `flush()` buffer runes, magic strings, paragraph markers, and active attributes.
- `setattr()` manages nested HTML tags for indent tables, headings, anchors, italic, bold, and constant-width text.
- `xcmd()` handles troff `x` commands for font mounting, resolution/type checks, inline HTML, man-page paragraph markers, headings, and man-reference anchors.
- `process()` parses troff output commands (`c`, `C`, `f`, `h`, `n`, `p`, `s`, `H`, `V`, `x`, etc.).
- `mountfont()` and `switchfont()` map troff font names to HTML styling bits.

Risk notes: the converter is tuned to `tmac.anhtml` conventions and uses heuristic indentation and line-break behavior.
