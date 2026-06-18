# File Research: sources/os/plan9/9front/sys/src/cmd/ql/compat.c

This file is a compatibility shim.

Contents:
- Includes `l.h`.
- Includes `../cc/compat`, pulling in shared C compiler/linker compatibility code by textual inclusion.

Usage:
- Keeps `ql` aligned with the shared Plan 9 compiler toolchain support code without duplicating it locally.

Implementation notes:
- The file has no local functions or data.
- Its behavior is entirely determined by the included compatibility source.
