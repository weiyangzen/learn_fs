# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.c

Purpose: implements binary halftone device color behavior and halftone tile-cache management for Ghostscript's imaging library.

Main components:
- Defines public device color type `gx_dc_type_ht_binary`.
- Provides GC pointer enumeration/relocation for binary halftone colors, tile arrays, and caches.
- Defines default cache sizing for small and large-memory builds.
- Allocates/frees `gx_ht_cache` with tile storage and bit buffers.
- Initializes tile cache layouts in `gx_ht_init_cache`.
- Renders halftone levels into cache tiles incrementally via `render_ht`.

Binary halftone color operations:
- `save_dc`: stores colors, level, component index, and phase.
- `get_dev_halftone`: returns the associated `gx_device_halftone`.
- `load`: switches cache order when needed, but defers tile rendering.
- `load_cache`: renders the needed level into the appropriate tile lazily.
- `fill_rectangle`: uses strip tiling or RasterOp copying depending on colors/source/lop.
- `fill_masked`: ensures cache loading, then delegates to default masked fill.
- `equal`: compares type, phase, colors, and halftone level.
- `write`/`read`: serializes/deserializes changed fields using flag bits and process color encoding.
- `get_nonzero_comps`: decodes both binary colors to identify components that can be nonzero.

Cache behavior:
- Cache levels are grouped into available tile slots.
- If all levels fit cheaply, tiles may be replicated horizontally and vertically to reduce repeated tiling overhead.
- Tile ids are generated from `gs_next_ids`.

Research notes:
- Several old tile-cache query functions are retained but return false/-1 with comments saying they are no longer used in DeviceN code.
- Read reconstruction always takes the halftone from `pis->dev_ht`; serialized data does not contain the tile or halftone object.
