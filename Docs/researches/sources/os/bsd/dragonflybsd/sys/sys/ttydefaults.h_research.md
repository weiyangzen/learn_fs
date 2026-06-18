# File Research: sources/os/bsd/dragonflybsd/sys/sys/ttydefaults.h

## Summary
System-wide default terminal mode and control-character definitions.

## Main Responsibilities
- Defines default input/output/local/control flags and default speed.
- Defines canonical default control characters through `CTRL()`.
- Optionally emits `static const cc_t ttydefchars[]` when `TTYDEFCHARS` is defined.
- Uses a static assertion to ensure the optional default control-character table matches `NCCS`.

## Important Behavior
`TTYDEF_LFLAG` defaults to canonical, signal, extended processing, and echo-related flags. Disabled control characters use `0xff` to avoid depending directly on `_POSIX_VDISABLE`.

## Risks
The optional table is included by macro side effect and then undefines `TTYDEFCHARS`. Consumers must include termios definitions consistently or the default table will not match the active control-character ordering.
