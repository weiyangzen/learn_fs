# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/venti.c

Purpose: Main Venti server executable.

Key behavior:
- Parses server options for addresses, config, web root, cache sizes, memory percentage, read-only mode, debug/foreground mode, logging, and queued writes.
- Loads config, bloom filter, sizes caches, initializes lump/index/disk caches, synchronizes the index, starts optional HTTP service and bloom/summing background tasks, then listens for Venti RPCs.
- `ventiserver` handles `VtTread`, `VtTwrite`, and `VtTsync` requests using `readlump`, `writelump`, and cache/queue flushes.
- Tracks RPC counters, byte counts, timing, cache hit/miss read timing, and failures.

Dependencies:
- Integrates almost all Venti server subsystems: config, index, bloom, caches, queues, HTTP, stats, tracing, and libventi server RPC.

Notable details:
- Automatic cache sizing uses observed free memory and subtracts bloom filter memory load.
- Read-only mode rejects writes and skips index synchronization.
