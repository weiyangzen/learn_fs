# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.h

Defines generic bitmap-cache entry, chunk, and cache structures.

Key definitions:
- `gx_cached_bits_head` stores total block size and depth; depth zero marks a free block.
- `gx_cached_bits_common` embeds the block head plus bitmap metadata: dimensions, shift, raster, and bitmap ID.
- `align_cached_bits_mod` ensures bitmap data following a cached-bits record satisfies bitmap, pointer, and long alignment requirements.
- `gx_bits_cache_chunk` stores a linked backing chunk with data pointer, size, and allocated byte count.
- `gx_bits_cache` stores the current chunk, allocation rover, total allocated bytes, and live entry count.
- Declares cache/chunk initialization, allocation, shortening, and free APIs.

Dependencies:
- Includes `gxbitmap.h` for bitmap IDs and alignment/raster concepts.
