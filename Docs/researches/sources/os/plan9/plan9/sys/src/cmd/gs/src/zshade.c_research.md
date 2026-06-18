# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zshade.c

LanguageLevel 3 shading and shading-pattern interface. It implements `currentsmoothness`, `setsmoothness`, `.shfill`, `.buildshading1` through `.buildshading7`, and `.buildshadingpattern`.

`zshfill` validates a non-executable shading structure and calls `gs_shfill`. `zbuildshadingpattern` combines a pattern dictionary, matrix, and shading object into a PatternType 2 pattern instance, using `int_pattern_alloc` for interpreter client data.

`build_shading` is the common dictionary framework. It copies the current non-Pattern color space into allocated shading parameters, reads optional `Background`, `BBox`, and `AntiAlias`, then calls a type-specific builder. `build_shading_function` builds either a single function or an array of functions combined with an Arrayed Output function; it enforces input-count compatibility. Indexed color spaces are rejected when a shading uses a function, matching the PLRM rule.

Type-specific builders cover Function-based, Axial, Radial, Free-form Gouraud triangle mesh, Lattice Gouraud triangle mesh, Coons patch mesh, and Tensor patch mesh shadings. Mesh support accepts array, file, or string `DataSource`, parses bit depths, decode arrays, optional functions, `BitsPerFlag`, and `VerticesPerRow` where relevant. Error paths release allocated functions, decode arrays, background colors, and copied color spaces.
