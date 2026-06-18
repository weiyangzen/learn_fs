# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.c

Small shared outline-character utility. `gs_char_flatness` derives a rendering flatness for outline fonts from the current CTM and a font default scale. It chooses the smallest meaningful CTM component, including off-diagonal terms for rotated/skewed matrices, rescales by `0.001 / default_scale`, clamps to the imager state’s flatness, and forces exact curve flattening for tiny characters by returning zero when the effective scale is below `0.2`.

This routine is used to make character outline rasterization quality less dependent on the current graphics-state flatness while preserving an upper bound. It depends on matrix-shape helpers from `gxfarith.h` and imager state definitions from `gxistate.h`.
