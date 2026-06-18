# File Research: sources/os/linux/linux/fs/jfs/jfs_mount.c

Implements JFS mount and read-write mount setup. It validates the aggregate superblock, opens special metadata inodes, initializes inode/block maps, opens the journal, marks the filesystem mounted, and writes a mount log record.

Mount flow:
- `jfs_mount()` calls `chkSuper()`, reads the aggregate inode map inode (`AGGREGATE_I`), mounts the aggregate inode map, reads and mounts the block map (`BMAP_I`), optionally reads/mounts the secondary aggregate inode map, and finally reads/mounts the fileset inode map (`FILESYSTEM_I`).
- Error paths unwind in reverse order using `diUnmount`, `diFreeSpecial`, and `dbUnmount`.

Read-write mount/remount:
- `jfs_mount_rw()` revalidates clean state on remount, truncates cached imap/bmap pages so fsck-updated maps are reread, remounts maps, opens the log with `lmLogOpen()`, updates the superblock to mounted/dirty state, and emits a `LOG_MOUNT` record.

Superblock handling:
- `chkSuper()` reads primary or secondary superblock through `readSuper()`, validates magic/version, enforces 4K JFS block size, checks state for read-write mounts, repairs in-memory flags for secondary AIT/AIM validity and group commit, computes JFS block geometry, copies UUID/log/fsck descriptors, and records inline/external log configuration.
- `updateSuper()` writes the mount state synchronously, with special `JFS_NOINTEGRITY` handling that preserves prior state externally while treating the live mount as dirty.
- `readSuper()` tries primary then secondary superblock offsets.

Journal mount record:
- `logMOUNT()` writes a `LOG_MOUNT` record with aggregate device identity. Recovery uses this boundary to avoid replaying older records for the same filesystem past the mount point.

Important invariants:
- Read-write mount requires clean filesystem state unless mounted read-only.
- JFS Linux support here requires `PSIZE` block size.
- Map initialization precedes journal activation; superblock dirtying follows successful journal open.
