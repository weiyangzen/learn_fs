# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runesprint.c

This file formats into an unbounded rune buffer.

Key behavior:
- `runesprint` delegates to `runevsnprint` with a very large bound.

Important details:
- Mirrors Plan 9 `sprint` behavior for rune strings.
