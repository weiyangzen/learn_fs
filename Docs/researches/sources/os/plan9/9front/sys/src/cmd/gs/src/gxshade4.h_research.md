# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade4.h

Internal declarations and compile-time tuning flags for triangle and patch shading rendering.

Key contents:
- Development/tuning flags for linear color procedures, quadrangle mode, interpatch padding, color contiguity, lazy wedges, visual trace, and no-fill/skip tests.
- Defines `mesh_frame_t`, `mesh_fill_state_t`, and common mesh fill-state macro with recursion frames.
- Defines wedge vertex list structures and lazy-wedge buffer sizing.
- Defines `patch_fill_state_t`, which extends mesh state with Function, vectorization, color-domain, flatness, smoothness, color linearity, self-intersection, and wedge allocation fields.
- Defines `patch_color_t`, `shading_vertex_s`, and `patch_curve_t`.
- Declares mesh/patch initialization, teardown, triangle fill, edge padding, patch fill, wedge-buffer allocation/free, color resolution, and background shading helper.

Notable dependencies:
- Consumes common shading types from `gxshade.h`.

Research notes:
- Comments describe interpatch padding as an Adobe-style trapping emulation using half-pixel expansion.
- `QUADRANGLES` support is retained mainly as historical/useful reference code but disabled because triangle decomposition looked better and faster.
- Several structures note missing GC descriptors, indicating this is internal transient rendering state rather than fully managed object state.
