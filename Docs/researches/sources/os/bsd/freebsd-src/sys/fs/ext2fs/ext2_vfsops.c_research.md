# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_vfsops.c

## Purpose
Implements FreeBSD VFS operations for ext2fs: mount/update/unmount, superblock parsing, group descriptor validation, vnode lookup, sync, statfs, NFS file handles, and metadata writeback.

## Main Elements
- Registers `ext2fs_vfsops` with mount, unmount, root, statfs, sync, vget, and fhtovp operations.
- `ext2_mount()` handles fresh mounts and updates, including read-only/read-write transitions, clean-state enforcement, GEOM access changes, reload, export handling, device lookup, and mount-from state.
- `ext2_check_sb_compat()` validates magic and rejects unsupported incompat/rocompat features for the requested access mode.
- `ext2_compute_sb_data()` derives in-memory geometry, validates block size, fragment size, inode size, group counts, descriptor size, free counts, checksums, and group descriptor layout.
- `ext2_cg_validate()` checks block bitmap, inode bitmap, and inode table placement per group, with flex-bg handling.
- `ext2_reload()` rereads superblock/group metadata and active inodes for read-only root reload after fsck.
- `ext2_mountfs()` opens the device through GEOM, reads the superblock, allocates mount state, initializes cluster summaries, marks write mounts dirty, and sets VFS flags.
- `ext2_unmount()` flushes vnodes, marks clean when appropriate, closes GEOM, releases root/device references, and frees all mount allocations.
- `ext2_sync()`, `ext2_sbupdate()`, and `ext2_cgupdate()` flush inode, superblock, and group descriptor state.
- `ext2_vget()` instantiates in-core inodes from on-disk dinodes and initializes vnodes.
- `ext2_fhtovp()` validates NFS file handles using inode number, generation, allocation state, and link count.

## Dependencies And Integration
Coordinates GEOM, buffer cache, vnode hashing, checksum helpers, inode conversion, allocation metadata, and ext2 vnode operations.

## Risk Notes
Mount-time validation is the main safety gate. Read-write mounts are denied for unclean filesystems unless forced, and unsupported feature masks must be kept aligned with actual implementation support.
