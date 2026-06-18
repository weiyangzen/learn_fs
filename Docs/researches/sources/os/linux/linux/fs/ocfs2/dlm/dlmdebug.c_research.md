# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.c

## Purpose
Provides diagnostic printing and debugfs views for OCFS2 DLM state: lock resources, locks, MLEs, purge lists, domain state, recovery state, and error names.

## Main Entry Points
- `dlm_print_one_lock_resource()` and `__dlm_print_one_lock_resource()` dump a lock resource and its granted/converting/blocked queues.
- `dlm_print_one_lock()` exports lock-resource printing for a lock handle.
- `dlm_errname()` maps `enum dlm_status` values to strings.
- `dlm_print_one_mle()` formats a master-list entry.
- `dlm_debug_init()` creates per-domain debugfs files.
- `dlm_create_debugfs_root()` / `dlm_destroy_debugfs_root()` manage `/sys/kernel/debug/o2dlm`.

## Debugfs Files
When `CONFIG_DEBUG_FS` is enabled, per-domain files are created:
- `dlm_state`: domain protocol, thread, node maps, resource counts, MLE counts, recovery state.
- `locking_state`: seq-file dump of tracked lock resources, including queues and LVB bytes.
- `mle_state`: current master-list entries and hash bucket statistics.
- `purge_list`: lock resources waiting on purge and age in seconds.

Without debugfs, the header supplies no-op inline functions.

## Formatting Helpers
`stringify_lockname()` contains OCFS2-specific knowledge to make dentry lock names more readable by decoding an inode block number. `stringify_nodemap()` prints node bitmaps. `dump_lockres()` emits compact machine-readable `NAME`, `LRES`, `RMAP`, `LVBX`, and `LOCK` records.

## Locking
Printing paths take the appropriate resource, DLM, master, tracking, AST, or lock spinlocks before traversing shared lists. The seq-file lockres iterator pins the current lock resource with `dlm_lockres_get()` and releases the previous one as iteration advances.
