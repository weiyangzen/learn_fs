# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_errlog.c

This file implements the persistent logical data error log for a pool. It combines on-disk ZAP logs with in-core AVL lists of pending errors.

Key behavior:
- Error keys are stringified `zbookmark_phys_t` tuples using `bookmark_to_name()` as `objset:object:level:blkid` in lowercase hex.
- Kernel builds also parse bookmark strings back with `name_to_bookmark()`.
- `spa_log_error()` ignores try-import loads, chooses the scrub or last pending AVL list based on scrub state, deduplicates by bookmark, and records new pending errors.
- `spa_get_errlog_size()` sums on-disk scrub and last logs plus in-core pending lists; the last log is skipped after scrub completion because it is about to rotate.
- Kernel-only `spa_get_errlog()` copies bookmarks to userland from on-disk logs and pending lists, using separate error-log and error-list locks to avoid recursion when reads themselves produce errors.
- `spa_errlog_rotate()` marks scrub completion so future errors go to the next list and `spa_errlog_sync()` performs actual log rotation.
- `spa_errlog_drain()` frees pending AVL entries, used when unloading a faulted pool whose errors cannot be synced.
- `sync_error_list()` creates a ZAP if needed, writes each bookmark as a key with an optional stored name string, then destroys the in-core list entries.
- `spa_errlog_sync()` copies pending lists under lock, clears `spa_scrub_finished`, then under `spa_errlog_lock` writes current errors, rotates logs after scrub completion, writes scrub errors, updates MOS directory entries, and commits an assigned TXG transaction.

Important invariants:
- The persistent view is the union of last log, scrub/current log, and pending lists.
- Pending list lock is dropped before writing ZAPs so I/O errors during errlog syncing can still be logged.
- On-disk logs are ZAP objects referenced by `DMU_POOL_ERRLOG_LAST` and `DMU_POOL_ERRLOG_SCRUB`.
