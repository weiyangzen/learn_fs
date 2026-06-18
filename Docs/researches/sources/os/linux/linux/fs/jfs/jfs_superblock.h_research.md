# File Research: sources/os/linux/linux/fs/jfs/jfs_superblock.h

Defines the on-disk JFS aggregate superblock layout and declares mount/superblock-facing functions.

`struct jfs_superblock` includes:
- Magic/version, aggregate size, logical and physical block sizes.
- Allocation group size, flags, state, compression flag.
- Secondary aggregate inode table/map descriptors.
- External log device/serial or inline log extent.
- Fsck workspace and service log fields.
- Extendfs staging fields.
- Volume UUID/label and external log UUID.

Constants:
- `JFS_MAGIC` is `"JFS1"`.
- `JFS_VERSION` is `2`.
- `LV_NAME_SIZE` preserves OS/2 boot-sector volume-name compatibility.

Exports:
- Superblock I/O/state: `readSuper`, `updateSuper`, `jfs_error`.
- Mount lifecycle: `jfs_mount`, `jfs_mount_rw`, `jfs_umount`, `jfs_umount_rw`, `jfs_extendfs`.
- Background task globals: `jfsIOthread`, `jfsSyncThread`.

Integration:
- Included by mount, unmount, log, metapage, and transaction code to share on-disk aggregate state and lifecycle hooks.
