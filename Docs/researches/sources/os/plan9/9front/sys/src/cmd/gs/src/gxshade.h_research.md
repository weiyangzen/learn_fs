# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.h

Internal declarations and algorithm notes for Ghostscript shading rendering.

Key contents:
- Documents parameter-space, color, and user-space mappings for shading types 1 through 7.
- Declares concrete shading wrapper structs for function-based, axial, radial, free-form Gouraud, lattice Gouraud, Coons patch, and tensor-product patch shadings.
- Declares fill-rectangle procedures for each shading type.
- Defines `shade_coord_stream_t`, which abstracts packed/array mesh data reading, decode, CTM conversion, and EOF state.
- Defines `mesh_vertex_t` and forward-declares `shading_vertex_t`.
- Declares stream helpers for flags, coordinates, colors, and vertices.
- Defines `shading_fill_state_common` and `shading_fill_state_t`, including device, imager state, direct color space, component count, and max color errors.
- Declares common fill-state initialization and `shade_fill_path`.

Notable dependencies:
- Public shading params from `gsshade.h`.
- Fixed and matrix types from `gxfixed.h`/`gxmatrix.h`.
- Ghostscript stream API.

Research notes:
- The header is unusually explanatory: it lays out the recursive subdivision strategy used by shading renderers.
- It notes that type 3 circle mappings are not closed under general CTM linear transforms in the same way as other shadings.
