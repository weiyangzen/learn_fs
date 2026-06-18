# File Research: sources/os/plan9/9front/sys/src/cmd/7l/compat.c

Tiny compatibility wrapper for the ARM64 linker.

Contents:
- Includes local linker declarations from `l.h`.
- Includes shared compiler compatibility code from `../cc/compat`.

There is no local logic. Its purpose is to pull the common Plan 9 compiler/linker compatibility implementation into the `7l` build.

Filesystem relevance: none directly; build support only.
