# File Research: sources/os/linux/linux/fs/tracefs/internal.h

Purpose: Shared internal declarations and data structures for tracefs/eventfs.

Contents:
- Tracefs inode flags: `TRACEFS_EVENT_INODE`, `TRACEFS_GID_PERM_SET`, `TRACEFS_UID_PERM_SET`, `TRACEFS_INSTANCE_INODE`.
- `struct tracefs_inode`: embeds VFS inode, list node, flags, and private pointer.
- `struct eventfs_attr`: saved mode/uid/gid for dynamic eventfs entries.
- `struct eventfs_inode`: children/list/RCU union, entry table, name, attr cache, data, kref, flags, entry count, inode number.
- `get_tracefs()` container helper.
- Prototypes for tracefs creation helpers and eventfs remount/release locking helpers.

Role:
- Defines the shared lifetime and metadata contract between `inode.c` and `event_inode.c`.
