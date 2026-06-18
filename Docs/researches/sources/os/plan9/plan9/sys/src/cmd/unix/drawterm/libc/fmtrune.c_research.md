# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtrune.c

This file appends one rune to a `Fmt`.

Key behavior:
- `fmtrune` emits a rune through the formatter's flush-aware output buffer.

Important details:
- Used by rune/string formatting helpers.
