# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpcache.h

Definition of the Ghostscript Pattern cache object.

Key contents:
- Forward declarations for `gx_pattern_cache` and `gx_color_tile`.
- `gx_pattern_cache_s` stores allocator, tile array, tile counts, round-robin index, current/max bitmap bit usage, and a `free_all` callback.
- Declares the private GC descriptor macro implemented in `gxpcmap.c`.

Notable dependencies:
- Uses Ghostscript memory and scalar types supplied by including context.

Research notes:
- The file documents the cache as an open hash table with single probing and round-robin replacement, with a note that both strategies could be improved.
- The cache data model is intentionally small and simple: no chaining, no reprobing, and fixed tile storage.
