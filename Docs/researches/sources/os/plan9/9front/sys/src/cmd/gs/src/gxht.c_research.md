# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.c

## Role

`gxht.c` implements Ghostscript binary halftone device color behavior and halftone tile cache management.

This is imaging/halftone rendering infrastructure, not filesystem code.

## Main Responsibilities

- Defines the public `gx_dc_type_ht_binary` device color type descriptor.
- Provides GC enumeration/relocation procedures for binary halftone device colors, tile arrays, and halftone caches.
- Allocates, initializes, clears, and frees halftone caches.
- Lazily renders halftone levels into cache tiles.
- Fills rectangles and masks with binary halftone textures.
- Serializes/deserializes binary halftone device colors for banding/high-level device workflows.
- Computes nonzero process components for binary halftone colors.

## Important Functions

- `gx_ht_cache_default_tiles` and `gx_ht_cache_default_bits`: choose small or large cache sizes based on memory/debug mode.
- `gx_ht_alloc_cache` and `gx_ht_free_cache`: allocate/free cache structure, bit storage, and tile array.
- `gx_ht_init_cache`: sizes tile replication, assigns cache ids, initializes per-tile strip bitmap metadata, and chooses a render dispatch path.
- `render_ht`: asks the order's render procedure to update a tile to a desired level and optionally replicates it horizontally/vertically.
- `gx_dc_ht_binary_load` and `gx_dc_ht_binary_load_cache`: bind a device color to the current halftone order and load the actual tile only at render time.
- `gx_dc_ht_binary_fill_rectangle` and `gx_dc_ht_binary_fill_masked`: render halftone fills through `strip_tile_rectangle`, `strip_copy_rop`, or the default masked-fill path.
- `gx_dc_ht_binary_write` and `gx_dc_ht_binary_read`: delta-serialize color0, color1, level, and component index.

## Data And Cache Semantics

- Cache capacity is limited by both tile count and bit-storage bytes.
- `levels_per_tile` maps multiple halftone levels to one cache tile when the cache cannot hold every level.
- Lazy tile loading avoids conflicts when multiple device colors share a small cache whose tiles can represent different levels at different times.
- The tile bitmap may be replicated horizontally and vertically to reduce tiling overhead when all renderings fit in cache.

## Notable Risks

- Several legacy helper routines (`gx_check_tile_cache_current`, `gx_check_tile_cache`, `gx_check_tile_size`) are stubs returning false or -1 and marked unused/not supported for DeviceN.
- `gx_dc_ht_binary_fill_rectangle` calls `gx_dc_ht_binary_load_cache` but ignores its return code, whereas the masked path checks it.
- Serialization omits the rendered tile and relies on the imager state's current device halftone during readback.
- Comments note a known wrong test around replicated tile raster/width in `render_ht`.
