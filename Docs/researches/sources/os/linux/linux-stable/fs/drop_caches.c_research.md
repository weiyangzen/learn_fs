# File Research: sources/os/linux/linux-stable/fs/drop_caches.c

## Purpose
`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl for manually dropping page cache and slab reclaimable objects.

## Sysctl
A write-only sysctl named `vm/drop_caches` accepts values from 1 to 4:
- bit 0: drop page cache
- bit 1: drop slab objects
- bit 2: suppress future informational logging

The handler is `drop_caches_sysctl_handler()`.

## Page Cache Dropping
`drop_pagecache_sb()` iterates a superblock’s inode list under `s_inode_list_lock`. It skips inodes being freed/new and, when rescheduling is not needed, skips mappings without pages.

For eligible inodes it:
1. Takes an inode reference with `__iget()`.
2. Drops the superblock inode-list lock.
3. Calls `invalidate_mapping_pages()`.
4. Releases the prior inode reference.
5. Calls `cond_resched()`.
6. Continues iteration.

## Slab Dropping
When bit 1 is set, the handler calls `drop_slab()` and records `DROP_SLAB`.

## Initialization
`init_vm_drop_caches_sysctls()` registers the sysctl table during `fs_initcall`.

## Notes
The global `sysctl_drop_caches` is intentionally simple. Page-cache dropping drains per-CPU LRU state first with `lru_add_drain_all()`.
