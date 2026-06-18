# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zshade.c

## Purpose
Implements LanguageLevel 3 shading operators, shading dictionary builders for ShadingTypes 1 through 7, and shading-pattern construction.

## Key Functions
- `zcurrentsmoothness()` and `zsetsmoothness()` expose smoothness state.
- `zshfill()` fills with an already built shading object.
- `zbuildshadingpattern()` builds PatternType 2 shading patterns.
- `build_shading()` collects common shading parameters and delegates type-specific construction.
- `build_shading_function()` builds single functions or array-composed functions.
- `build_shading_1()` through `build_shading_7()` build function-based, axial, radial, triangle mesh, lattice mesh, Coons patch, and tensor patch shadings.
- `build_directional_shading()` parses shared axial/radial parameters.
- `build_mesh_shading()` parses mesh data sources, decode arrays, and optional functions.
- `flag_bits_param()` parses mesh flag bits where relevant.

## Important Behavior
- Shading color space is copied from the current graphics color space; Pattern space is rejected.
- Optional `Background`, `BBox`, and `AntiAlias` are common to all shading types.
- Indexed color spaces are rejected when a shading has a `Function`, matching PLRM/Adobe behavior.
- Mesh data sources may be arrays of floats, files, or strings.
- Stream/string mesh data requires `BitsPerCoordinate`, `BitsPerComponent`, and `Decode`; free-form, Coons, and tensor meshes also require `BitsPerFlag`.
- On failure, allocated functions, decode arrays, backgrounds, and color spaces are released.

## Research Notes
Large LL3 rendering front end that converts PostScript shading dictionaries into Ghostscript shading structures.
