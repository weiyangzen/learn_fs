# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/util.c

Purpose: provides shared fsck helpers for inode writing, cluster allocation accounting, inode type lookup, per-slot system file iteration, resource statistics, I/O cache sizing, bitmap wrappers, and emergency abort.

Read coverage: complete file read, 493 lines.

Key responsibilities:
- Wraps inode writes with `i_blkno` sanity checking and fsck error-state updates.
- Marks clusters allocated/unallocated in fsck’s in-memory allocation bitmap and creates the duplicate-cluster bitmap on first collision.
- Counts bits in byte arrays for group descriptor free-bit validation.
- Reads an inode to map mode bits to OCFS2 directory entry file type.
- Iterates all slots for a given system inode type and applies a callback.
- Tracks per-pass wall/user/system time and I/O/cache statistics, then aggregates and prints optional stats.
- Initializes libocfs2 I/O cache based on requested cache mode, available memory, filesystem size, and journal estimates.
- Provides bounded pre-cache accounting with `o2fsck_worth_caching()` and `o2fsck_reset_blocks_cached()`.
- Wraps bitmap set/clear failures as fatal fsck aborts.
- Aborts by sending SIGTERM to the current process so fsck signal handlers can clean up.

Important entry points:
- `o2fsck_write_inode()`
- `o2fsck_mark_cluster_allocated()`, `o2fsck_mark_clusters_allocated()`, `o2fsck_mark_cluster_unallocated()`
- `o2fsck_type_from_dinode()`
- `o2fsck_bitcount()`
- `handle_slots_system_file()`
- `o2fsck_init_resource_track()`, `o2fsck_compute_resource_track()`, `o2fsck_add_resource_track()`, `o2fsck_print_resource_track()`
- `o2fsck_init_cache()`, `o2fsck_worth_caching()`, `o2fsck_reset_blocks_cached()`
- `__o2fsck_bitmap_set()`, `__o2fsck_bitmap_clear()`, `o2fsck_abort()`

Dependencies:
- Uses libocfs2 bitmap, cached I/O, inode, system inode, cluster conversion, and I/O stats APIs.
- Uses POSIX `getrusage`, `gettimeofday`, `sysconf`, `getpagesize`, `kill`, and process signal handling.

Risk and edge cases:
- Duplicate cluster bitmap allocation failure aborts the process immediately because later repair depends on that tracking.
- Cache sizing intentionally limits use to a fraction of available physical pages and retries with smaller allocations.
- `o2fsck_print_resource_track()` protects against negative computed walltime but can still divide by very small elapsed time.
- Fatal bitmap wrapper errors call `o2fsck_abort()` rather than returning, so callers rely on process-level cleanup.
