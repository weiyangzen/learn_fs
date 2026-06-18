# File Research: sources/os/linux/linux-stable/fs/nfsd/filecache.c

## Summary
Implements the NFSD open file cache. It caches `struct file` objects by inode, credential, network namespace, access mode, and GC policy, with separate behavior for precisely owned opens and reusable garbage-collected opens.

## Main APIs
- `nfsd_file_cache_init()`, `nfsd_file_cache_shutdown()`, per-net start/shutdown/purge helpers.
- `nfsd_file_acquire_gc()`, `nfsd_file_acquire()`, `nfsd_file_acquire_opened()`, `nfsd_file_acquire_local()`, `nfsd_file_acquire_dir()`.
- `nfsd_file_get()`, `nfsd_file_put()`, `nfsd_file_put_local()`.
- `nfsd_file_close_inode_sync()`, `nfsd_file_is_cached()`, `nfsd_file_cache_stats_show()`.

## Behavior
Cache entries are stored in an `rhltable` keyed by inode pointer and protected by RCU plus inode lock during insertion. Pending entries serialize concurrent construction with `NFSD_FILE_PENDING`. GC-enabled entries retain an LRU reference after final user put, allowing reuse until the laundrette or shrinker evicts them. Fsnotify marks and lease notifiers close cached files when conflicting filesystem events occur.

## State and Synchronization
Uses a global list-LRU, shrinker, delayed laundrette work, fsnotify group, lease notifier, per-net disposal queues, and percpu counters. File release closes the backing file, checks writeback errors, releases fsnotify marks, unhashes, and frees via RCU.

## Risks
The cache intentionally stores `nf_inode` without taking an inode reference, so it must only be used as a comparison key. Refcounting is subtle around LRU-held references, pending construction failures, localio installed pointers, and delayed per-net disposal.
