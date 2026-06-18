# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex.c

Purpose: Command-line wrapper for synchronizing a Venti index.

Key behavior:
- Loads config and bloom filter, initializes disk/lump/index caches, optionally prints the index, calls `syncindex`, then flushes caches.
- Supports `-B` disk cache memory, `-I` index cache memory, and `-v`.

Dependencies:
- Uses `initventi`, `loadbloom`, `initdcache`, `initlumpcache`, `initicache`, `syncindex`, and cache flush helpers.

Notable details:
- Allocates a small 1 MiB lump cache for the maintenance run.
