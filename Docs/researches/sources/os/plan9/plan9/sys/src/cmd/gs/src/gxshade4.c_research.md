# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.c

`gxshade4.c` renders Gouraud triangle mesh shadings.

`mesh_init_fill_state` initializes common shading fill state, stores the mesh shading pointer, and records the fixed clipping rectangle.

`Gt_next_vertex` decodes the next vertex through `shade_next_vertex`; if the mesh has a Function, it treats the decoded color as a function parameter and evaluates the Function into actual color components.

`Gt_fill_triangle` creates a temporary `patch_fill_state_t`, initializes it, optionally paints interpatch padding along the triangle edges, then calls `mesh_triangle`. It terminates patch state afterward.

`gs_shading_FfGt_fill_rectangle` handles free-form triangle meshes. It reads flags from the coordinate stream: flag 0 starts a fresh triangle, flag 1 reuses the previous second/third vertices in one pattern, and flag 2 reuses them in another. Each completed triangle is filled.

`gs_shading_LfGt_fill_rectangle` handles lattice-form meshes. It reads the first row into an allocated vertex array, then streams subsequent vertices to form pairs of triangles between adjacent rows. The vertex array is freed on exit.

Errors propagate from decoding, allocation, function evaluation, and triangle fill. EOF handling differs by mode: free-form checks stream EOD after flag read failure, lattice loops on stream EOF.
