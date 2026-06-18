# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c

Implements ext2 filesystem-level VFS operations: init, mount, reload, unmount, statfs, sync, vnode lookup, file handles, and metadata updates.

Key entry points:
- `ext2fs_init()` initializes inode/dinode pools and delegates common UFS init.
- `ext2fs_mountroot()`, `ext2fs_mount()`, and `ext2fs_mountfs()` attach ext2 filesystems.
- `ext2fs_reload()` reloads read-only mounted filesystem metadata after fsck.
- `ext2fs_unmount()` flushes, marks clean when possible, closes the device, and frees mount data.
- `ext2fs_statfs()` computes free blocks/files and overhead.
- `ext2fs_sync()` flushes dirty vnodes, device buffers, group descriptors, and superblock.
- `ext2fs_vget()` materializes vnodes/inodes from inode-table blocks.
- `ext2fs_fhtovp()` and `ext2fs_vptofh()` implement NFS file-handle conversion.
- `ext2fs_sbupdate()` and `ext2fs_cgupdate()` write superblock and group descriptors.
- `e2fs_sbcheck()` validates magic, block size, revision, feature compatibility, and journal recovery state.

Important behavior:
- Mounting read-write marks a clean filesystem dirty; unmount/sync can mark it clean again if no errors remain.
- Unsupported incompat features reject the mount; ext4 read-only incompat features force read-only operation.
- `e2fs_sbfill()` computes in-memory geometry and loads all group descriptors.
- Large-file limits are derived from logical indirect capacity and physical block counters, with special handling for huge-file and extent features.
- `ext2fs_vget()` reconstructs 32-bit uid/gid from split ext2 fields and resets deleted inodes to mode/size zero.
- Generation numbers are assigned on old filesystems when absent.

Dependencies:
- Shares UFS mount structure (`ufsmount`) and generic UFS operations.
- Uses ext2 endian load/save helpers, group descriptor helpers, pools, buffer cache, and vnode iteration APIs.

Watch points:
- `ext2fs_reload()` calls `e2fs_sbfill()` to allocate group descriptors after copying a new superblock; the old descriptor allocation is not freed in this function.
- `e2fs_sbcheck()` allows journal recovery-needed filesystems only for read-only mount attempts.
- `ext2fs_sync()` panics if it sees modified state on a read-only filesystem.
