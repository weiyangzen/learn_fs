# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/input.c

Implements the input stack for `htmlroff`.

Key points:
- `Istack` entries represent input from files, strings/macros, or stdin, with unget buffers, line numbers, names, and pop callbacks.
- Supports pushing immediate input or queueing input after the current bottom entry.
- `pushinputfile`/`queueinputfile` open named files as `Biobuf`s.
- `pushstdin`/`queuestdin` bind stdin through a duplicate fd.
- `pushinputstring` pushes rune-string input, mainly for macros, strings, and register expansion.
- `inputnotify` installs a callback called when the current input source is popped.
- `getrune` pulls from unget, string, or file input, updates line numbers, and pops exhausted inputs.
- `ungetrune` supports up to three pushed-back runes, creating an empty string input if needed.
- `linefmt` reports the active file-backed input and line for diagnostics.
- `setlinenumber` updates the visible file name/line, supporting `.lf`.

Dependencies and interactions:
- Used by `roff.c`, macro expansion in `t7.c`, file switching in `t19.c`, and diagnostics.
- Maintains `.F` and `.B` number/string registers when file input changes.

Research relevance:
- This file is the source-location and input-composition layer for the roff interpreter.
