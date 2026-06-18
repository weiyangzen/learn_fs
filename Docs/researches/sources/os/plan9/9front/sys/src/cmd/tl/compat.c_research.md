# File Research: sources/os/plan9/9front/sys/src/cmd/tl/compat.c

This file only includes linker headers:

- `#include "l.h"`
- `#include "../cc/compat"`

Purpose:
- Pulls shared compiler compatibility support into the `tl` build.

Risk notes:
- The include path lacks `.h` on `../cc/compat`, matching Plan 9 source conventions.
