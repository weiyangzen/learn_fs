# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dofmt.c

This file is the core byte-string formatter for Plan 9 `Fmt`.

Key behavior:
- `dofmt` parses format strings, flags, width, precision, argument indexes, and dispatches conversions.
- Helper conversions include chars, runes, strings, rune strings, integers, counts, percent, flags, and bad-format output.
- `__fmtflush`, `__fmtpad`, `__rfmtpad`, `__fmtcpy`, and `__fmtrcpy` manage buffered output and padding.

Important details:
- Supports Plan 9 format flags and length modifiers, including `ll`, `l`, `h`, `u`, `#`, width, precision, and left adjustment.
- Conversion dispatch is supplied by `fmt.c`.
