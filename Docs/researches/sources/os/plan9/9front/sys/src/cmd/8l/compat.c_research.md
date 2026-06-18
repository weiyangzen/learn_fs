# File Research: sources/os/plan9/9front/sys/src/cmd/8l/compat.c

This tiny file includes linker definitions and the shared C compiler compatibility implementation.

Key responsibilities:
- Includes `l.h`.
- Includes `../cc/compat`, making shared compatibility routines part of the `8l` build.

Integration points:
- Allows the linker to reuse host/platform compatibility helpers used by the compiler and assembler family.

Risks and invariants:
- This is an include-wrapper source file; its behavior is entirely determined by the included compatibility body.
