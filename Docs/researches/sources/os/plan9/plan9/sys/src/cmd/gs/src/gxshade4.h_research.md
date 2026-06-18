# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade4.h

`gxshade4.h` defines internal triangle and patch shading rendering state.

Development flags control linear color procedures, triangle vs quadrangle decomposition, interpatch padding, color-contiguity subdivision, lazy wedge generation, and visual-debug/testing modes. Production-relevant defaults include triangle decomposition, half-pixel interpatch padding, and lazy wedges.

`mesh_frame_t` stores recursion vertices and clipping state. `mesh_fill_state_t` extends common shading fill state with mesh shading pointer, clip rect, recursion depth, and a fixed-size recursion frame stack.

Lazy wedge support uses linked `wedge_vertex_list_elem_t` nodes and lists to defer boundary wedge creation until neighboring areas are known. This reduces redundant wedge fills along shared subdivision boundaries.

`patch_fill_state_t` extends mesh fill state with Function pointer, vectorization flags, color argument count, coordinate/flatness/smoothness controls, self-intersection and color-linearity flags, wedge-buffer ownership, and color domain data.

`patch_color_t`, `shading_vertex_t`, and `patch_curve_t` represent parametric colors, mesh/patch vertices, and Bezier patch boundaries. The header declares fill-state lifecycle, triangle fill, padding, patch fill, wedge-buffer allocation/free, color resolution, and shade-background helper.

This is a shared private contract for `gxshade4.c`, `gxshade1.c`, and patch-rendering implementation files.
