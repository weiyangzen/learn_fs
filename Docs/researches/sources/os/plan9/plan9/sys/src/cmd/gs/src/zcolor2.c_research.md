# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor2.c

Implements a small Level 2 color helper.

Key behavior:
- `.usealternate` returns true when the current color space has and uses a base/alternate color space, as detected by `cs_base_space`.

Dependencies and coupling:
- Level 2-only operator table.
- Relies on graphics color-space inspection from `gxcspace.h` / `gscolor2.h`.
