# File Research: sources/os/plan9/9front/sys/src/cmd/2l/compat.c

Purpose: tiny compatibility inclusion unit for linker `2l`.

Key contents:
- Includes `l.h`.
- Includes shared common compiler/linker compatibility implementation from `../cc/compat`.

Research notes:
- This file exists to compile the common compatibility body into the linker with `2l`’s declarations visible.
