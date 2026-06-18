# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.h

Declares NV-cache state, chunk metadata, compactor state, throttling parameters, and management/recovery entry points.

Important definitions:
- `FTL_NVC_VERSION_CURRENT` is version 2.
- `FTL_NV_CACHE_NUM_COMPACTORS` is 8.
- Throttle constants define 20 ms update intervals and a proportional modifier clamped between -0.8 and 0.5.
- `ftl_chunk_state` models `FREE`, `OPEN`, `CLOSED`, and `INACTIVE`.

`struct ftl_nv_cache_chunk_md` is exactly one FTL block and stores version, open/close sequence IDs, write/read/compaction pointers, state, P2L tail-map checksum, P2L IO log type, and reserved space.

`struct ftl_nv_cache` owns bdev handles, mempools, chunk lists/counters, compactor list, sequence state, free targets, compaction bandwidth SMA, and throttle accounting.

Public functions cover init/deinit, read/write, metadata fill, chunk-map access, state save/load, halt/resume checks, tail metadata sizing, recovery management hooks, address lookup, trim sequence acquisition, and chunk metadata initialization.
