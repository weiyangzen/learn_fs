# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor3.c

## Purpose
LanguageLevel 3 color operator support for smoothness and shaded fills.

## Key Behavior
- `gs_setsmoothness` clamps and stores smoothness in the graphics state.
- `gs_currentsmoothness` returns the stored value.
- `gs_shfill` constructs a shading pattern, marks it as an `shfill`, remaps it as a Pattern color, converts the current clipping path into a path, and fills that path.

## Important Details
- The comment explains that `shfill` is implemented through `gs_fill`-style path filling to preserve high-level output behavior.
- The generated pattern intentionally disregards shading Background for `shfill` semantics.
- Pattern references are released after the fill.

## Dependencies
Uses pattern type 2 support, shading structures, clip-path conversion, path filling, pattern remapping, and graphics-state internals.

## Research Notes
This is color/shading rendering glue, not device or filesystem code.
