# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_init.c

Read completely: 160 lines.

Initializes core VFS infrastructure and declares the statically configured filesystem type table for the kernel build.

Filesystem registration:
- `vfsconflist[]` contains compile-time `struct vfsconf` entries for enabled filesystems such as FFS, MFS, EXT2FS, CD9660, MSDOSFS, NFS client, NTFS, UDF, FUSE, and TMPFS.
- Each entry records VFS ops, mount type name, numeric type id, flags such as `MNT_LOCAL` and `MNT_SWAPPABLE`, and expected mount-argument size.
- `maxvfsconf` is initialized to the table length, then recomputed as the highest configured type number during initialization.

Initialization and lookup:
- `vfsinit()` initializes `namei_pool`, vnode tables, the namecache, and each filesystem's optional `vfs_init()` hook.
- It also sets `maxvfsconf` based on configured type numbers.
- `vfs_byname()` returns a `vfsconf` by mount type name.
- `vfs_bytypenum()` returns a `vfsconf` by numeric filesystem type.

Risks and notes:
- This is static registration; missing compile-time options omit filesystem support entirely.
- `namei_pool` uses fixed `MAXPATHLEN` buffers and is shared by pathname resolution.
- Type numbers are sparse and must remain ABI-compatible with userland and mount interfaces.
- Filesystem `vfs_init()` hooks run during global VFS initialization and must tolerate early boot context.
