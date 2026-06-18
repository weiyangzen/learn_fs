# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_syscall.c

## Purpose
Provides a lint-only variadic stub for `syscall`.

## Key Elements
Includes `<stdarg.h>` and `<unistd.h>` and defines `syscall(int arg1, ...)` returning `0`.

## Dependencies
Consumed by libc lint generation/checking.

## Behavior/Risks
No runtime behavior; it exists to make lint understand the public variadic syscall interface.
