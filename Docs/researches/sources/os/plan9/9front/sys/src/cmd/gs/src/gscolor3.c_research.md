# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.c

## Role

`gscolor3.c` implements Ghostscript LanguageLevel 3 color operations for smoothness and shading fill.

This is rendering/shading infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setsmoothness`
- `gs_currentsmoothness`
- `gs_shfill`

## Core Behavior

`gs_setsmoothness` clamps the graphics-state smoothness value to `[0,1]`.

`gs_shfill` constructs a shading pattern from the supplied shading object, marks it as a `shfill` pattern, remaps it through a Pattern color space without a base space, converts the current clipping path into a path, and fills that path with winding rule. It then releases the pattern reference.

The implementation deliberately uses `gx_fill_path` rather than direct shading fill so high-level output devices can observe the fill operation.

## Dependencies

Uses Pattern Type 2 support, shading support, clip-path-to-path conversion, device color remapping, and graphics state/path operations.

## Notable Risks

- `gs_shfill` allocates and remaps a pattern before converting/filling the clip path; each failure path must preserve pattern reference cleanup.
- Background handling is described in comments, but this function does not visibly clone and remove `Background`; that behavior likely occurs through `gs_pattern2_set_shfill`.
