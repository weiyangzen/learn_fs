# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpcache.h

`gxpcache.h` defines the rendered Pattern cache object. It forward-declares `gx_pattern_cache` and `gx_color_tile`.

`gx_pattern_cache_s` stores the allocator, tile array, tile count, used tile count, next round-robin replacement index, used bit budget, maximum bit budget, and a `free_all` callback. The header comment describes the design as an open hash table with single probing and round-robin replacement.

`private_st_pattern_cache()` supplies GC metadata for the `tiles` pointer; implementation and cache operations live in `gxpcmap.c`.

The structure is intentionally simple and low-level. Cache keys and values are in `gx_color_tile_s` from `gxpcolor.h`. The main limitation is direct id modulo indexing with no reprobing, so collisions evict existing entries aggressively.
