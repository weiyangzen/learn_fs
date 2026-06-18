# File Research: sources/os/linux/linux-stable/fs/tracefs/internal.h

Purpose: Internal tracefs/eventfs shared declarations and data structures.

Key responsibilities:
- Defines tracefs inode flags for eventfs, gid/uid permission overrides, and instance directories.
- Defines `struct tracefs_inode`, embedding the VFS inode plus tracefs metadata.
- Defines `struct eventfs_attr` for saved mode/uid/gid.
- Defines `struct eventfs_inode` metadata for dynamic eventfs directories and files.
- Provides `get_tracefs()` container helper.
- Declares tracefs creation lifecycle helpers and eventfs remount/dentry release hooks.

Important interactions:
- Used by both tracefs core and eventfs dynamic inode code.
- Encodes the private contract for remount propagation and eventfs lazy materialization.

Notable invariants and risks:
- `tracefs_inode` fields after `vfs_inode` are zeroed by cache initialization.
- `eventfs_inode` uses bitfields for freed/events state and entry count.
