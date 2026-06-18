# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000hwgc.c

Registers hardware cursor eligibility for ET4000-W32. `init` marks itself initialized, then disables hardware cursor globally via `cflag` unless the active controller name starts with `et4000-w32`, the mode is 8 bpp, and 2x8-bit pixel mode is not active.

It does not program cursor registers directly; it gates later hwgc selection in `main.c`.
