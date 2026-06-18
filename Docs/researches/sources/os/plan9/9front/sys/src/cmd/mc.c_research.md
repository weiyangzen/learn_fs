# File Research: sources/os/plan9/9front/sys/src/cmd/mc.c

Implements `mc`, a columnation utility that reads lines from files/stdin and prints them in multiple columns sized to the output width.

Key behavior:
- Supports `-` for colon-sensitive breaks, `-LINEWIDTH` to force width, and `-t` in the option table though `tabflag` is effectively controlled by display probing.
- Reads input into a dynamically grown Rune buffer, expands tabs to spaces, and splits words at newlines.
- Computes column count from maximum word width and line width, using pixel widths when a display font is available.
- Auto-detects Acme/window text width and tab stop using `/dev/acme/ctl`, `$font`, `/dev/window`, and `$tabstop`.
- Emits columns row-wise, padding with tabs or spaces.

Important dependencies: Plan 9 `bio`, `draw`, fonts, `/dev/acme`, `/dev/window`.

Notable risks:
- Input is fully buffered before columnation except colon-triggered flushes.
- `morechars()` depends on `nchars` to restore `cbufp` after realloc.
