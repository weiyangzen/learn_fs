# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_pfs.c

Purpose: implements HAMMER pseudo-filesystem ioctl operations. PFS ids are mapped to localization bits, and most entry points accept an inode only as context for autodetecting a default PFS id.

Key entry points:
- `hammer_ioc_get_pseudofs()` autodetects the PFS, loads in-memory PFS state, reports current `hammer_pseudofs_data`, and for master PFSs refreshes `sync_end_tid` from `flush_tid1`.
- `hammer_ioc_set_pseudofs()` copies user-supplied PFS data into the in-core PFS, creates a root inode when switching/creating a master PFS, persists it, and wakes waiters on `sync_end_tid`.
- `hammer_ioc_upgrade_pseudofs()` unloads cached PFS state, rolls a slave back to `sync_end_tid + 1`, clears the slave flag, and saves it.
- `hammer_ioc_downgrade_pseudofs()` marks a master as slave and advances `sync_end_tid` to at least `flush_tid1`.
- `hammer_ioc_destroy_pseudofs()` rolls the PFS back with `trunc_tid == 0` and marks it deleted.
- `hammer_ioc_wait_pseudofs()` sleeps until either a slave PFS `sync_end_tid` or master `flush_tid1` has advanced past the requested value.
- `hammer_ioc_scan_pseudofs()` directly scans the root misc PFS record without using the cached PFS RB tree.

Important internals: `hammer_pfs_autodetect()` validates ids and user buffer size. `hammer_pfs_rollback()` performs a mirror-filtered backend B-tree scan over the PFS localization and applies rollback edits through `hammer_pfs_delete_at_cursor()`: records created at or after the truncation TID are destroyed, while records deleted at or after the truncation TID are undeleted by adjusting `delete_tid` to zero.

Concurrency and recovery behavior: long rollback scans call `hammer_signal_check()` and return ioctl interruption via `HAMMER_IOC_HEAD_INTR`; they also pause on metadata/UNDO pressure using flusher waits. Cursor retry handles `EDEADLK`. PFS upgrades/destroys intentionally unload cached PFS state before mutation.

Research notes: this file is the PFS state-control layer, not the root PFS record serializer itself. It relies heavily on common HAMMER cursor deletion semantics and mirror-filtered scans to make slave promotion safe after partial mirror syncs.
