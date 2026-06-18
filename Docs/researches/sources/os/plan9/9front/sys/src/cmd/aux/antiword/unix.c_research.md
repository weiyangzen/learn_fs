# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/unix.c

Unix approximation layer for RISC OS functions.

Key responsibilities:
- Implements `werr()` by printing to `stderr` and optionally exiting.
- Provides no-op `Hourglass_On()` and `Hourglass_Off()` functions for shared rendering code.

Important behavior:
- `iFatal == 0` is warning-only.
- `iFatal == 1` exits with `EXIT_FAILURE`; other fatal values exit with that code.

Research relevance:
- Keeps portable code independent of platform-specific error/progress APIs.
