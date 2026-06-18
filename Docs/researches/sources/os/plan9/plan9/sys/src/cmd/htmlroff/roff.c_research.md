# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/roff.c

`roff.c` is the central htmlroff interpreter loop. It owns the dispatch tables for normal requests (`Req`), raw requests (`Raw`), and escape handlers (`Esc`), plus global parser controls such as `dot`, `tick`, `backslash`, `inputmode`, conditional state, output paragraph state, and current line position.

Key behavior:
- `addreq`/`delreq`/`renreq`, `addraw`/`delraw`/`renraw`, and `addesc` register troff request and escape handlers used by the `t*.c` modules.
- `getnext` reads logical input characters, expands registered escapes depending on mode, handles `Uformatted`/`Uunformatted` diversion sentinels, and preserves escapes in argument/copy contexts when needed.
- `copyarg`, `readline`, and `parseargs` implement request argument reading, quote handling, and troff comment stripping.
- `dotline` dispatches control lines to raw handlers, regular builtins, or user-defined macros.
- `runinput` is the main lexer/interpreter loop; it recognizes request lines at beginning of line, handles newline semantics, starts paragraph output, and emits runes.
- `startoutput` maps current number registers into HTML paragraph style attributes for line height, margins, indent, and alignment.
- `outrune` and `outhtml` convert internal pseudo-runes and normal runes into escaped HTML output.

Important dependencies:
- Requires `t1init` through `t20init`, `htmlinit`, macro support, number/string registers, input stack helpers, and output globals from `a.h` and sibling files.
- `run()` intentionally does not call `t9init` and `t12init`, with comments noting those source files.

Notable risks/quirks:
- Dispatch tables have fixed caps (`MAXREQ`, `MAXRAW`, `MAXESC`) and only warn on overflow.
- Output formatting is approximate troff-to-HTML translation, not layout-faithful.
- `ungetnext` only pushes one rune and admits it cannot fully undo compound escape reads.
