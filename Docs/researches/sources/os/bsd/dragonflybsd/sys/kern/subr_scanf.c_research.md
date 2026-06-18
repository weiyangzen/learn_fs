# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_scanf.c

## Summary
Provides compact kernel `sscanf` support for scanning from an in-memory string.

## Main Responsibilities
- `ksscanf()` wraps `kvsscanf()`.
- `kvsscanf()` parses literals, whitespace, width, suppression, `h/hh/l/q` length modifiers, `%d/%i/%o/%u/%x/%p`, `%s`, `%c`, `%[...]`, and `%n`.
- Uses `strtoq` / `strtouq` for numeric conversion after collecting a bounded token.
- `__sccl()` builds scanset character-class tables.

## Important Behavior
Numeric conversion uses a fixed 32-byte token buffer. `%i` performs base autodetection; `%p` is treated as hexadecimal pointer input. Return values follow scanf-style assigned count, match failure, and input failure behavior.

## Risks
Callers must provide adequately sized destination buffers for `%s`, `%c`, and scansets. Floating-point flags exist in comments/macros but floating conversions are not implemented. Scanset range behavior intentionally preserves old V7-compatible quirks.
