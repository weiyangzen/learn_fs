# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor2.c

This is a small Level 2 color operator file.

Key behavior:
- Implements `.usealternate`, which pushes true when the current color space has a base or alternate color space in use.
- Uses `cs_base_space(gs_currentcolorspace(igs))` to detect that condition.

Important dependencies:
- Uses color-space APIs from `gxcspace.h` and `gscolor2.h`.
- Registered as Level 2 in `zcolor2_l2_op_defs`.

Research notes:
- This is a narrow interpreter helper for Separation/alternate color-space behavior.
