# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgcache.c

## Role

Glyph data cache implementation, currently specialized for Type 42 font glyph data read from files.

## Main Data

Defines `gs_glyph_cache_elem` with cached `gs_glyph_data_t`, glyph index, lock count, and list link. Defines `gs_glyph_cache` with total size, list head, stable memory allocator, Type42 font, stream, and read callback.

## Control Flow

`gs_glyph_cache__alloc` allocates cache state in stable memory and registers a font-free notification. `gs_glyph_cache__release` frees all cached glyph data, unregisters notification, and frees the cache. Lookup scans the list for matching glyphs or an unlocked recyclable element. `gs_get_glyph_data_cached` loads missing glyph data through the callback, recycles old unlocked entries after an arbitrary size threshold, moves hits to the head, and returns a locked client `gs_glyph_data_t` view.

## Dependencies

Uses Type42 font internals, glyph data API, stream, font notifications, and Ghostscript GC descriptors.

## Notes

Substring on cached glyph data is unsupported and returns `unregistered`; freeing a client view only decrements the cache element lock count.
