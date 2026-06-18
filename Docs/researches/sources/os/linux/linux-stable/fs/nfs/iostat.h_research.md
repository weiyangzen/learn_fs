# File Research: sources/os/linux/linux-stable/fs/nfs/iostat.h

## Purpose
Defines per-mount NFS client I/O statistics storage and lightweight per-CPU accounting helpers.

## Main Types and Helpers
- `struct nfs_iostats`
  - Per-CPU structure with byte counters indexed by `__NFSIOS_BYTESMAX`.
  - Event counters indexed by `__NFSIOS_COUNTSMAX`.
  - Cacheline aligned to reduce contention.
- `nfs_inc_server_stats()` / `nfs_inc_stats()`
  - Increment per-server or inode-derived event counters using `this_cpu_inc()`.
- `nfs_add_server_stats()` / `nfs_add_stats()`
  - Add byte counts using `this_cpu_add()`.
- `nfs_alloc_iostats()`
  - Macro wrapping `alloc_percpu(struct nfs_iostats)` so allocation tagging remains distinct.
- `nfs_free_iostats()`
  - Frees non-NULL per-CPU stats.

## Dependencies
Uses public NFS iostat enum definitions from `<linux/nfs_iostat.h>` and relies on `NFS_SERVER(inode)->io_stats`.

## Research Notes
The file is intentionally header-only for hot-path accounting. It has no locking because it uses per-CPU counters.
