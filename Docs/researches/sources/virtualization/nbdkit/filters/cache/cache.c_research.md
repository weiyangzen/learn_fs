# File Research: sources/virtualization/nbdkit/filters/cache/cache.c

Purpose: main nbdkit cache filter that layers a local temporary block cache over a backend plugin.

Key details:
- Global configuration includes `cache=writeback|writethrough|unsafe`, `cache-min-block-size`, optional reclaim thresholds, and `cache-on-read`.
- `cache_on_read` supports static boolean mode or path-triggered mode.
- `.get_ready` initializes the block cache; `.prepare` forces early size discovery and cache sizing.
- `.block_size` advertises cache-friendly preferred size while preserving backend constraints.
- Overrides `.can_cache` to native because this filter handles caching.
- Overrides `.can_fast_zero` to advertise support but rejects fast zero attempts.
- `cache_pread` handles unaligned heads/tails with temporary buffers and delegates block reads to `blk.c`.
- `cache_pwrite` performs read-modify-write for unaligned writes, handles FUA emulation, and flushes when needed.
- `cache_zero` implements zero by writing zero-filled blocks into the cache rather than calling backend `.zero`.
- `cache_flush` scans dirty blocks, writes them through, then flushes the backend unless in unsafe mode.
- `cache_cache` rounds cache requests outward to whole cache blocks and explicitly caches them.
- Multi-connection semantics are forced true for writeback/unsafe and delegated in writethrough mode.

Risk notes:
- Writeback/unsafe semantics intentionally decouple backend persistence from client writes.
- All block operations depend on the global mutex; this is simple and safe but limits parallelism.
