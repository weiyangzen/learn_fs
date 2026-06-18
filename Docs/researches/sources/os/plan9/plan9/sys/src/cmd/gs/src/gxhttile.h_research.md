# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxhttile.h

Purpose: defines the cacheable halftone tile record used by device colors and halftone caches.

Main type:
- `gx_ht_tile` wraps a `gx_strip_bitmap` plus cache metadata.

Fields:
- `tiles`: rendered strip bitmap for the current halftone tile.
- `level`: cached gray/halftone level, or `-1` when cache is empty by convention.
- `index`: tile index inside the cache, used for relocation/GC logic.

Dependencies:
- Requires `gxbitmap.h` definitions before inclusion.

Research notes:
- This header is deliberately small so clients of `gx_device_color` can see halftone tile layout without pulling in the full halftone cache internals.
