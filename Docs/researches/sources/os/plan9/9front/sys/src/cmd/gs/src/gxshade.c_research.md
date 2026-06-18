# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxshade.c

Common shading rendering support: packed mesh data decoding, shading fill-state initialization, and path fill helper.

Key behavior:
- `shade_next_init` initializes a `shade_coord_stream_t` over a reusable stream, string, or array data source, selecting packed or array value decoders.
- `cs_next_packed_value` reads arbitrary-width packed unsigned integers across byte boundaries and marks EOF on short reads.
- `cs_next_array_value` reads float values from unpacked arrays and validates integer range when flags/packed values are requested.
- Decoding functions convert packed integers through Decode ranges or pass array floats through directly.
- `shade_next_flag` byte-aligns packed input before reading a flag.
- `shade_next_coords` reads coordinate pairs, decodes them, and transforms them through the current CTM to fixed device points.
- `shade_next_color` handles Indexed color lookup, direct component decode, or single function argument input.
- `shade_next_vertex` reads one mesh vertex and initializes a second color argument defensively.
- `shade_init_fill_state` chooses direct/base color space, computes per-component smoothness/error tolerances, and accounts for device color/halftone capacity.
- `shade_fill_path` fills a path using the target device with shading-specific fill params.

Notable dependencies:
- Color spaces and indexed/CIE/ICC support: `gxcspace.h`, `gscindex.h`, `gscie.h`, `gsicc.h`.
- Device/client and halftone state: `gxdevcli.h`, `gxistate.h`, `gxdht.h`.
- Fill and shading internals: `gxpaint.h`, `gxshade.h`, `gxshade4.h`.

Research notes:
- `MAX_SMOOTHNESS` clamps overly high smoothness to avoid blocky output.
- Function-based shadings with non-monotonic functions are noted in `gxshade.h` as not fully handled by the smoothness test.
