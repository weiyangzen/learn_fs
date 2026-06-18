# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.h

Purpose: Defines generic bitmap-cache structures used by higher-level caches such as character or tile caches.

Key definitions:
- `gx_cached_bits_head` stores block size and depth; `depth == 0` means free.
- `gx_cached_bits_common` embeds bitmap metadata: width, height, shift, raster, and bitmap ID.
- `align_cached_bits_mod` ensures cached bitmap payload alignment.
- `gx_bits_cache_chunk` stores chunk linkage, byte data, total size, and allocated bytes.
- `gx_bits_cache` stores current chunk, allocation rover, total bytes, and entry count.

Declared API:
- `gx_bits_cache_init()`
- `gx_bits_cache_chunk_init()`
- `gx_bits_cache_alloc()`
- `gx_bits_cache_shorten()`
- `gx_bits_cache_free()`

Dependencies:
- Includes `gxbitmap.h` for bitmap/raster ID and alignment definitions.

Notable risks:
- Header is intentionally key-agnostic; users must maintain hash/list structures and remove entries before freeing blocks.
