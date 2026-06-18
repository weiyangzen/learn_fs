# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmt.c

This file manages the global format-conversion registry and dispatch.

Key behavior:
- `fmtinstall` installs conversion functions by verb.
- `fmtfmt` looks up conversion handlers.
- `__fmtdispatch` calls `dofmt` or `dorfmt` based on byte versus rune format strings.
- Initializes default conversions for integers, strings, chars, runes, floats, quotes, and errors.

Important details:
- Uses a small fixed table plus locking hooks.
- `PLAN9PORT` conditionals support hosted variants.
