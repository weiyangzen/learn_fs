# File Research: sources/os/linux/linux/fs/tracefs/event_inode.c

Purpose: Implements eventfs, the dynamic tracefs subtree used for tracing events. It stores metadata and creates dentries/inodes just in time.

Key APIs:
- `eventfs_create_events_dir()` creates the top-level events directory.
- `eventfs_create_dir()` creates child eventfs metadata directories.
- `eventfs_remove_dir()` and `eventfs_remove_events_dir()` remove metadata and invalidate persistent event dentries.
- `eventfs_remount()` updates saved ownership after tracefs remount.
- `eventfs_d_release()` releases eventfs_inode references held by dentries.
- `eventfs_remount_lock()` / `eventfs_remount_unlock()` coordinate tracefs remount with eventfs SRCU/mutex.

Implementation notes:
- `eventfs_inode` metadata tracks children, file entry table, per-entry saved attrs, default attr, data pointer, kref, freed/events flags, entry count, and stable inode number.
- Top-level events dir uses `eventfs_root_inode`, adding a persistent `events_dir` dentry pointer.
- File and directory dentries are created during lookup/readdir using callbacks in `eventfs_entry`.
- All event files use synthetic inode number `EVENTFS_FILE_INODE_INO`; directories lazily allocate stable inode numbers.
- Attribute changes are cached back into eventfs metadata so dynamic dentries preserve user changes.

Concurrency and correctness:
- `eventfs_mutex` protects mutation and freed-state checks.
- `eventfs_srcu` protects traversal/lifetime after removal from parent lists.
- `kref` is driven by dentry `d_fsdata` references; final release calls per-entry `release` callbacks and frees after SRCU.
- Removal is recursive and capped by expected events/group/event/file depth.
- Lookup callbacks run under eventfs locking, and comments warn callbacks must not re-enter tracefs/eventfs.
