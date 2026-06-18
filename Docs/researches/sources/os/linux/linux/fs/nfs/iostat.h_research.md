# File Research: sources/os/linux/linux/fs/nfs/iostat.h

## Purpose
Defines per-mount NFS client I/O statistics storage and lightweight per-CPU accounting helpers.

## Main Types and Helpers
- `struct nfs_iostats` stores byte counters and event counters indexed by public NFS iostat enums, cacheline-aligned.
- `nfs_inc_server_stats()` / `nfs_inc_stats()` increment event counters using `this_cpu_inc()`.
- `nfs_add_server_stats()` / `nfs_add_stats()` add byte counts using `this_cpu_add()`.
- `nfs_alloc_iostats()` wraps `alloc_percpu(struct nfs_iostats)` as a macro for allocation tagging.
- `nfs_free_iostats()` frees non-NULL per-CPU stats.

## Dependencies
Uses `<linux/nfs_iostat.h>` for counter indexes and expects `NFS_SERVER(inode)->io_stats` to point at allocated per-CPU storage.

## Research Notes
Header-only hot-path accounting. Locking is avoided because all updates are per-CPU.
