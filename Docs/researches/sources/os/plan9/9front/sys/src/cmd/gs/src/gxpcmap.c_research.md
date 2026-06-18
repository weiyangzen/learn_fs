# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcmap.c

Pattern color mapping, rendering, accumulation, and caching implementation for PatternType 1 colors.

Key behavior:
- Provides default Pattern cache sizing, with smaller defaults for small-memory/debug configurations.
- Defines GC descriptors for color tiles, cache entries, pattern accumulators, and related device structures.
- Implements a pattern accumulator forwarding device that renders colored pattern bits and/or a 1-bit mask into memory devices.
- Accumulator drawing procs update color bits when present and update mask coverage for fills, mono copies, and color copies.
- `gx_pattern_alloc_cache` creates a fixed-size tile table and initializes tile keys/data pointers.
- `gx_pattern_cache_free_entry` releases cached tile bitmaps and updates `bits_used`/`tiles_used`.
- `gx_pattern_cache_add_entry` strips all-ones masks, evicts by hash slot and round-robin size pressure, transfers bitmap ownership from accumulator devices into cache tiles, and records pattern metadata.
- `gx_pattern_cache_add_dummy_entry` records a device-managed high-level pattern placeholder.
- `gx_pattern_load` checks cache, renders the pattern PaintProc into an accumulator device, adds it to the cache, then closes/free states.
- `gs_pattern1_remap_color` handles colored and uncolored PatternType 1 remapping and loads the pattern tile/mask.

Notable dependencies:
- Pattern/color internals: `gxpcolor.h`, `gxp1impl.h`, `gxcolor2.h`, `gxdcolor.h`.
- Device/memory devices: `gxdevice.h`, `gxdevmem.h`.
- Graphics state: `gzstate.h`.

Research notes:
- `pattern_accum_get_bits_rectangle` notes that unread areas should use the mask but currently do not.
- The cache indexes by `id % num_tiles`; collisions evict the existing slot.
- `gx_pattern_load` has multiple ownership transitions: accumulator close normally frees bookkeeping, but cached bitmap buffers are preserved by clearing memory pointers.
