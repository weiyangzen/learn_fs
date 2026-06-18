# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_cache.c

## Role

`vdev_cache.c` implements the historical per-vdev read-ahead cache, also called the software track buffer. It inflates small metadata reads into larger aligned reads, stores them in an LRU cache, and serves later nearby reads from memory.

The implementation remains present but is disabled by default: `zfs_vdev_cache_size = 0`.

## Main Behavior

Cache structure:
- Each vdev has a `vdev_cache_t` with a lock, an AVL tree by offset, and an AVL tree by last-used tick.
- Cache blocks are `1 << zfs_vdev_cache_bshift`, defaulting to 64 KiB.
- Reads larger than `zfs_vdev_cache_max`, reads crossing cache-block boundaries, and reads with `ZIO_FLAG_DONT_CACHE` bypass the cache.
- Kstats track delegations, hits, and misses.

Operations:
- `vdev_cache_allocate()` reserves a placeholder entry before the fill I/O completes, preventing multiple threads from issuing the same read.
- `vdev_cache_read()` handles hits, in-flight fill delegation, and misses. On a miss, it creates a delegated read zio for the whole cache block and adds the original zio as a child.
- `vdev_cache_fill()` copies data to all waiting parent zios when the fill completes, then evicts the line if the fill failed or a write raced with the fill.
- `vdev_cache_write()` updates cached lines after writes, or marks in-flight lines with `ve_missed_update`.
- `vdev_cache_purge()`, `vdev_cache_init()`, and `vdev_cache_fini()` manage lifecycle.

## Integration Notes

The cache is below DMU semantics and above physical vdev I/O. It uses ABD buffers, delegated zios, AVL ordering, and per-vdev locking. Its hits use `zio_vdev_io_bypass()` so the original physical I/O does not proceed.

## Risk Notes

- Because the cache is disabled by default, changes may be rarely exercised in normal deployments.
- In-flight fill plus concurrent write handling depends on `ve_missed_update`; incorrect behavior can return stale data.
- LRU eviction refuses to evict entries with active fill I/O.
- Cache sizing uses global tunables, so enabling it can increase read amplification and memory consumption.
- ABD copy offsets must match cache phase and I/O offsets exactly.
