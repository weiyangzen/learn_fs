# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/venti.c

`venti.c` is the Venti server entry point. It parses server address, HTTP address, config path, memory/cache sizing, readonly, logging, queueing, and webroot flags; loads config and bloom filter; sizes lump/block/index caches; starts HTTP, cache, bloom, arena sum, and optional write-queue services; synchronizes the index; then listens for Venti RPCs.

Automatic memory sizing reads `/dev/swap`, subtracts bloom-filter load impact, enforces conservative minima, and caps values to avoid signed 32-bit overflow in older internals. Config values, command-line cache sizes, and `-m` percentage sizing have explicit precedence.

`ventiserver()` handles `Tread`, `Twrite`, and `Tsync`, updating stats and using `readlump()`, `writelump()`, queue flush, and cache flush. On shutdown it flushes disk and index caches.
