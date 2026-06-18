# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dorfmt.c

This file is the rune-format-string counterpart to `dofmt`.

Key behavior:
- `dorfmt` parses a `Rune*` format string and dispatches conversions through the same `Fmt` machinery.

Important details:
- Enables `Rune` output formatting APIs.
