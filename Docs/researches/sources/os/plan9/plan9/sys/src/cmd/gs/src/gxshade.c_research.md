# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxshade.c

`gxshade.c` implements shared shading support: decoding mesh data streams and initializing fill state.

`shade_next_init` prepares a `shade_coord_stream_t` from a shading mesh data source. It supports reusable streams, strings wrapped in a local stream, and array sources. It selects packed or array value/decoded readers and initializes EOF/bit-buffer state.

Packed reads use `cs_next_packed_value`, which consumes arbitrary bit widths from a byte stream and reports rangecheck on EOF. Array reads use floats and validate integer range when reading flags or packed integer-like values. Decoded reads map packed integers through Decode ranges; array decoded values are used directly.

`shade_next_flag`, `shade_next_coords`, `shade_next_color`, and `shade_next_vertex` decode flags, transformed fixed-point coordinates, color components, Indexed color lookups, and full mesh vertices.

`shade_init_fill_state` computes common recursive fill tolerances from smoothness, device color capacity, halftone levels, shading type, and CIE/ICC ranges. It resolves Indexed spaces to direct base spaces. `shade_fill_path` fills one generated path through the device `fill_path` proc with shading-specific params.

This file is the common substrate for mesh, axial, radial, and patch shading renderers.
