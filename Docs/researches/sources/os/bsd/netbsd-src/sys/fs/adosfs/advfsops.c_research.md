# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/advfsops.c

## Summary
Implements ADOSFS VFS operations: mount, unmount, root lookup, statvfs, vnode loading, bitmap loading, file-handle conversion, sync, init/done, and module attach/detach.

## Main Responsibilities
- Enforce read-only mounting.
- Resolve and authorize block device mounts.
- Open the device, derive geometry from disklabel/partition data, and read the boot block `dostype`.
- Validate DOS type, compute root block, block counts, block sizes, data block size, and mount stat fields.
- Load root vnode through `VFS_ROOT()`.
- Load and count allocation bitmap free blocks, freeing the bitmap for read-only mounts.
- Load `anode` data from on-disk blocks, including directories, files, hard links, and symlinks.
- Convert AmigaDOS symlink syntax to Unix-style paths.
- Register VFS operations and sysctl node.

## Key Interfaces
- `adosfs_mount()`, `adosfs_mountfs()`, `adosfs_unmount()`, `adosfs_root()`, `adosfs_statvfs()`.
- `adosfs_vget()`, `adosfs_loadvnode()`.
- `adosfs_loadbitmap()`.
- `adosfs_fhtovp()`, `adosfs_vptofh()`.
- `adosfs_init()`, `adosfs_done()`.

## Risks
Mount correctness depends on disklabel fields and boot block format. `adosfs_loadvnode()` parses many fixed offsets from AmigaDOS blocks; malformed media can produce invalid names, link targets, block chains, or permissions. The filesystem is read-only, but still exposes NFS file handles without generation validation.
