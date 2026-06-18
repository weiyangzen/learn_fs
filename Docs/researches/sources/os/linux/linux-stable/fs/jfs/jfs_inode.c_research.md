# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_inode.c

This file provides JFS inode flag translation and new inode allocation/initialization.

Key responsibilities:
- Translates JFS on-disk/private mode flags to VFS inode flags in `jfs_set_inode_flags()`, including immutable, append-only, no-atime, dirsync, and sync.
- Allocates a new VFS inode in `ialloc()`.
- Calls `diAlloc()` to allocate the corresponding JFS disk inode number and inode extent metadata.
- Inserts the inode into the inode cache with `insert_inode_locked()`.
- Initializes ownership, saved uid/gid, quotas, inherited JFS flags, directory/file/symlink-specific mode flags, timestamps, generation number, and JFS private fields.
- Handles allocation failure paths by dropping quotas, clearing link count, discarding new inodes, or releasing the inode.

Important interactions:
- Bridges VFS inode creation and the JFS inode map allocator in `jfs_imap.c`.
- Uses quota initialization/allocation after disk inode allocation and before returning the live inode.
- Relies on JFS mount-wide generation state (`gengen`) and parent `mode2` inheritance.
- Exports flag state used by VFS permission and write paths through `inode_set_flags()`.

Notable invariants and risks:
- Disk inode allocation occurs before quota allocation; later failures must unwind both VFS and quota state correctly.
- New directories set `IDIRECTORY` and clear inherited `JFS_DIRSYNC_FL`, while non-directories default to inline EA and sparse support.
- Symlinks explicitly drop immutable/append inheritance.
- `jfs_inode->mode2` combines private high-order flags with the VFS mode bits.

Research notes:
- This is the small but important handoff from VFS object creation into JFS-specific disk inode allocation and private inode initialization.
