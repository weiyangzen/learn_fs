# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfs_vfsops.c

## Summary
Implements NetBSD VFS-level operations for msdosfs: module registration, mount/update/root-mount handling, boot sector and BPB validation, mount control block initialization, FAT geometry setup, in-use map initialization, unmount, root lookup, statvfs, sync, and NFS file-handle conversion.

## Main Responsibilities
- Define the `msdosfs_vfsops` table and module attach/detach entry point.
- Register the msdosfs sysctl node.
- Normalize and apply mount options in `update_mp()`, including legacy argument compatibility, GMT offset handling, GEMDOS behavior, long-name/short-name policy, and name length reporting.
- Mount root from `root_device` with default msdosfs arguments.
- Implement `msdosfs_mount()` for argument retrieval, update mounts, device lookup, block-device permission checks, device open, `msdosfs_mountfs()` invocation, and statvfs metadata setup.
- Parse and validate FAT boot sector/BPB fields in `msdosfs_mountfs()`, including sector size, sectors per cluster, FAT size, FAT type, FAT32 FSInfo, GEMDOS transformations, cluster count, FAT block sizing, and max block size limits.
- Allocate and populate `struct msdosfsmount`, set mount flags/shifts/sizes, build `pm_inusemap` via `msdosfs_fillinusemap()`, and mark the block device mounted.
- Unmount by flushing vnodes, closing the device, destroying file-handle state, and freeing mount/FAT allocation structures.
- Return the root vnode with `msdosfs_root()`.
- Report capacity/free-space metadata through `msdosfs_statvfs()`.
- Sync dirty denodes and the device vnode through `msdosfs_sync()`.
- Convert between file handles and vnodes with `msdosfs_fhtovp()` and `msdosfs_vptofh()`.

## Key Interfaces
- `msdosfs_vfsops`.
- `msdosfs_mountroot(void)`.
- `msdosfs_mount(struct mount *, const char *, void *, size_t *)`.
- `msdosfs_mountfs(struct vnode *, struct mount *, struct lwp *, struct msdosfs_args *)`.
- `msdosfs_unmount(struct mount *, int)`.
- `msdosfs_root(struct mount *, int, struct vnode **)`.
- `msdosfs_statvfs(struct mount *, struct statvfs *)`.
- `msdosfs_sync(struct mount *, int, kauth_cred_t)`.
- `msdosfs_fhtovp(struct mount *, struct fid *, int, struct vnode **)`.
- `msdosfs_vptofh(struct vnode *, struct fid *, size_t *)`.
- `msdosfs_vget(struct mount *, ino_t, int, struct vnode **)`, currently unsupported.

## Risks
Mount validation is security- and stability-sensitive because malformed BPB fields drive shift counts, FAT sizing, cluster counts, and buffer sizes. The boot signature check is disabled for compatibility with real-world media, so later consistency checks carry more responsibility. Read-write upgrades depend on device permission checks and mount flag transitions. FSInfo validation is partial and may disable FSInfo use. `msdosfs_sync()` panics if a read-only mount is marked modified. NFS file handles rely on directory cluster/offset plus generation state maintained outside this file.
