# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.c

Rendering front-end for Gouraud triangle mesh shadings, including free-form and lattice forms. It decodes vertices and delegates actual triangle/padding rendering to patch/mesh helpers.

Key behavior:
- `mesh_init_fill_state` initializes common shading fill state and stores the clipping rectangle.
- `Gt_next_vertex` reads a shading vertex and, if a Function is present, treats the decoded component as a function input and evaluates it into actual color components.
- `Gt_fill_triangle` creates a `patch_fill_state_t`, optionally emits interpatch padding on all triangle edges, then calls `mesh_triangle`.
- `gs_shading_FfGt_fill_rectangle` reads free-form Gouraud mesh flags. Flag `0` reads a fresh triangle; flags `1` and `2` reuse prior vertices according to PostScript mesh semantics.
- `gs_shading_LfGt_fill_rectangle` allocates one row of vertices, then consumes subsequent rows to generate two triangles per lattice cell.
- Visual trace hooks wrap triangle patch rendering when enabled.

Notable dependencies:
- Mesh stream decoding from `gxshade.c`/`gxshade.h`.
- Patch/mesh fill helpers from `gxshade4.h`.
- Color/function support: `gsptype2.h`, `gxcspace.h`, `gxdcolor.h`.

Research notes:
- Free-form mesh parsing returns `rangecheck` for invalid flags and verifies that loop termination was actual end-of-data.
- Lattice mesh rendering frees its row buffer through a single `out` path.
- This file does not define `mesh_triangle`, `mesh_padding`, or patch fill internals; it is the type-4/type-5 decoder/front-end.
