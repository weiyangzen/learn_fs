# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/unix.c

This file provides Unix replacements for a small set of RISC OS UI/platform functions.

Key behavior:
- `werr()` prints warnings/errors to `stderr` and exits for fatal severities.
- Defines no-op `Hourglass_On()` and `Hourglass_Off()`.

Important details:
- Fatal code `1` maps to `EXIT_FAILURE`; other fatal values are used as process exit codes.

Filesystem relevance:
- Minimal: reports errors for file operations performed elsewhere.
