# File Research: sources/os/linux/linux/fs/drop_caches.c

## Role

`drop_caches.c` implements the `/proc/sys/vm/drop_caches` sysctl for manually dropping page cache and/or slab caches.

## Page Cache Dropping

`drop_pagecache_sb()` iterates a superblock’s inode list, skips inodes in freeing/new states and usually skips empty mappings, takes a temporary inode reference, drops the superblock inode-list lock, invalidates mapping pages, releases the previous inode reference, and reschedules as needed.

The delayed `toput_inode` avoids dropping the final reference while holding the superblock inode-list lock.

## Sysctl Handler

`drop_caches_sysctl_handler()` uses `proc_dointvec_minmax()` for writes in the range 1 through 4. On write:
- bit 1 drains LRU additions and invalidates page cache for all superblocks
- bit 2 calls `drop_slab()`
- bit 4 suppresses future informational logging

VM events are counted for pagecache and slab drops.

## Registration

`drop_caches_table` registers write-only `drop_caches` under `vm` during `fs_initcall()`.

## Important Behaviors and Invariants

- This is an explicit manual cache drop path, not normal reclaim.
- Inode references and lock dropping are arranged to avoid inode-list deadlocks.
- The sysctl variable is global and intentionally simple.

## Research Notes

Read completely. This file is standalone VFS/MM sysctl glue outside DLM.
