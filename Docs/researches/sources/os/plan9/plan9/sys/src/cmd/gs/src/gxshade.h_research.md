# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.h

`gxshade.h` declares internal shading-rendering types and APIs. It documents the parameter-space mappings for PDF/PostScript shading types 1 through 7 and the general recursive subdivision strategy.

The header defines concrete shading structs for function-based, axial, radial, free-form Gouraud triangle, lattice-form Gouraud triangle, Coons patch, and tensor-product patch shadings, each with a fill-rectangle procedure declaration.

`shade_coord_stream_t` stores a stream wrapper, bit buffer, EOF flag, mesh params, CTM, and function pointers for reading values and decoded floats. It is used by mesh renderers to consume packed, string, stream, or array data sources.

`mesh_vertex_t` stores fixed position plus float color components, while `shading_vertex_t` is forward-declared for the triangle/patch header to define.

The common fill state macro stores device, imager state, direct color space, component count, and per-component maximum color error. Public helpers initialize stream/fill state, decode flags/coordinates/colors/vertices, and fill generated shading paths.

This header is the bridge between generic shading setup and specialized renderer implementations in `gxshade1.c`, `gxshade4.c`, and related patch files.
