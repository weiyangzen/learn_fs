# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vfsops.c

## Role

Implements DragonFly VFS operations for mounting, unmounting, syncing, exporting, and statting MSDOSFS volumes. It parses the FAT boot sector/BPB, derives filesystem geometry, initializes the mount control block, builds the in-use cluster bitmap, and wires MSDOSFS vnode operations into the mount.

## Major Entry Points

- `msdosfs_mount()` handles initial mounts, update mounts, read-only/read-write transitions, device lookup, permission checks, export updates, and mount stat population.
- `mountmsdosfs()` opens the backing disk, validates the boot sector, computes FAT12/FAT16/FAT32 geometry, allocates `msdosfsmount`, and fills the in-use cluster map.
- `msdosfs_unmount()` flushes vnodes, closes the device, releases iconv handles, frees FAT/mount memory, and clears device mount state.
- `msdosfs_root()` returns the root denode vnode.
- `msdosfs_statfs()` and `msdosfs_statvfs()` report FAT cluster counts and free-space state.
- `msdosfs_sync()` flushes dirty denodes, device metadata, and FSInfo state.
- `msdosfs_fsiflush()` writes FAT32 FSInfo free-cluster and next-free hints.
- `msdosfs_fhtovp()`, `msdosfs_checkexp()`, and `msdosfs_vptofh()` support NFS export file handles.

## Implementation Notes

- `update_mp()` applies owner/group/mode masks, mount flags, and optional kernel iconv conversion handles.
- FAT32 detection is based on zero root directory entries, nonzero big FAT sectors, and compatible FS version fields.
- The mount code validates sector size, sectors-per-cluster power-of-two constraints, FAT sector count, total sector count, overflow, and maximum block size compatibility.
- Cluster count determines FAT12 versus FAT16 when the BPB did not already imply FAT32.
- FAT block I/O size is tuned separately: FAT12 uses `3 * 512`, while other FAT types use `PAGE_SIZE`, rounded to physical sector size.
- `pm_bpcluster`, `pm_crbomask`, `pm_cnshift`, and `pm_bnshift` provide the offset/block conversion basis used throughout the filesystem.
- FAT32 FSInfo is trusted only if all three signatures match; otherwise it is ignored.
- `fillinusemap()` requires `pm_devvp` and `pm_dev` to be installed before scanning the FAT.
- `MNT_SYNCHRONOUS` maps to `MSDOSFSMNT_WAITONFAT`.
- The sync scanner calls `VOP_FSYNC()` on dirty denode vnodes and repeats while rescans are requested.

## Dependencies

Uses DragonFly VFS mount/update/unmount APIs, device vnode operations, buffer cache, FAT BPB/boot-sector structures, denode and FAT allocation code, kernel iconv, netexport, and VFS vnode scanning.

## Research Notes

The file is the mount-time geometry authority for MSDOSFS. Most lower-level FAT macros and vnode operations rely on fields initialized here, especially cluster size, root directory location, FAT width, and the in-use cluster bitmap.
