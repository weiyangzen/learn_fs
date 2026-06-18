# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_vfsops.c

## Purpose

`msdosfs_vfsops.c` implements the FreeBSD VFS operations for FAT/MS-DOS filesystems: mount argument translation, mount/update/remount handling, boot-sector and BPB parsing, FAT geometry initialization, root vnode lookup, statfs, sync, NFS file-handle conversion, unmount cleanup, and emergency read-only remount after detected metadata corruption.

## Main Entry Points

- `msdosfs_cmount()` converts legacy `struct msdosfs_args` from userland into named mount arguments such as `from`, `uid`, `gid`, masks, charset names, long/short-name options, and iconv options before calling `kernel_mount()`.
- `msdosfs_mount()` validates mount options, handles MNT_UPDATE read-only/read-write transitions, resolves and checks the device vnode, calls `mountmsdosfs()` for new mounts, and applies per-mount user-visible options through `update_mp()`.
- `mountmsdosfs()` opens the GEOM provider, reads the boot sector, validates BPB fields, computes FAT12/16/32 geometry, initializes the in-use cluster bitmap, marks writable volumes dirty, counts fixed-root free directory entries, and installs mount data.
- `msdosfs_unmount()` suspends writes for writable mounts, flushes vnodes, marks the volume clean, closes iconv handles, closes the GEOM provider, releases device references, destroys the FAT lock, and frees mount state.
- `msdosfs_root()`, `msdosfs_statfs()`, `msdosfs_sync()`, and `msdosfs_fhtovp()` provide the VFS root/stat/sync/export hooks used by the kernel.
- `msdosfs_integrity_error()` and `msdosfs_remount_ro()` implement asynchronous forced read-only remount after corruption-sensitive failures.

## Data And State

The file allocates `M_MSDOSFSMNT` for `struct msdosfsmount` and `M_MSDOSFSFAT` for the FAT allocation bitmap. `mountmsdosfs()` fills all key `msdosfsmount` fields: device vnode/provider references, BPB values, FAT size and block layout, root directory block/size, first data cluster, max cluster, sector/cluster shift values, FAT masks/multipliers, FSInfo location, next-free cluster hint, free-cluster bitmap, root directory free-entry count, flags, and the FAT lock/taskqueue context.

The VFS operation vector registered by `VFS_SET(msdosfs_vfsops, msdosfs, 0)` exposes `.vfs_fhtovp`, `.vfs_mount`, `.vfs_cmount`, `.vfs_root`, `.vfs_statfs`, `.vfs_sync`, and `.vfs_unmount`.

## Mount And Remount Behavior

The update path distinguishes read-write to read-only and read-only to read-write transitions. Downgrading to read-only suspends writes, flushes writable vnodes, marks the volume clean while the provider is still writable, drops the GEOM write reference, clears `pm_fmod`, sets `MSDOSFSMNT_RONLY`, and sets `MNT_RDONLY`. Upgrading verifies write access or mount privilege on the original device vnode, gains a GEOM write reference, marks the volume dirty via `markvoldirty_upgrade()`, then clears the read-only flags.

For a new mount, the code accepts device mounts only, checks VREAD/VWRITE permissions or `PRIV_VFS_MOUNT_PERM`, protects against multiple mounts by atomically setting `dev->si_mountpt`, opens the provider through GEOM, and sets `BO_NOBUFS` on the original device vnode buffer object while the mounted filesystem owns device buffering.

`update_mp()` applies charset/iconv options and ownership/mask/name-mode flags. If `nowin95` is set, it forces short-name mode; otherwise it defaults to long-name mode. Charset conversion handles are opened only when `kiconv` is requested and `msdosfs_iconv` is available.

## FAT Geometry And Validation

`mountmsdosfs()` reads the boot sector, optionally checks boot signatures, initializes DOS 5 style BPB fields, and then fixes FAT32-specific fields from the FAT32 BPB extension. Validation checks include nonzero bytes-per-sector and sectors-per-cluster, power-of-two sector and cluster sizing, minimum sector size, nonzero total and FAT sectors, maximum cluster size within `MAXBSIZE`, volume size not exceeding provider media size, total sectors past first cluster, and FAT capacity not exceeded by the computed maximum cluster.

FAT type is selected from BPB layout and cluster count. FAT32 uses a root-directory cluster and FSInfo block; FAT12/FAT16 use a fixed root directory between the FAT area and first data cluster. FAT12 uses a 3/2 FAT byte addressing ratio and a smaller FAT block size chosen to avoid split entries. FAT16 and FAT32 use page-sized FAT blocks rounded to the device sector size.

The FSInfo block is trusted only if its signatures match. The next-free hint is clamped to a valid cluster range, and the free-count field is ignored because the implementation scans the FAT into `pm_inusemap`.

## Sync, Stat, And Export Semantics

`msdosfs_statfs()` reports clusters as blocks and uses `pm_freeclustercount` for both free and available blocks. File counts are meaningful mainly for the fixed FAT12/FAT16 root directory; FAT32 sets root-directory free entries to zero.

`msdosfs_sync()` scans every vnode on the mount, skips clean or lazy-only vnodes, nonblocking-locks dirty vnodes, calls `VOP_FSYNC()`, then fsyncs the device vnode for non-lazy sync and flushes FAT32 FSInfo through `msdosfs_fsiflush()`. On `MNT_SUSPEND`, it sets `MNTK_SUSPEND2 | MNTK_SUSPENDED` after successful flushing.

`msdosfs_fhtovp()` maps exported file handles containing directory cluster and directory offset back to denodes via `deget()`, then creates a vnode VM object sized to `de_FileSize`.

## Dependencies

This file depends on FreeBSD VFS, vnode, mount, namei, privilege, buffer cache, taskqueue, and GEOM APIs. msdosfs-specific dependencies include BPB/boot-sector structures, denodes, FAT helpers, `fillinusemap()`, `markvoldirty()`, `markvoldirty_upgrade()`, `deget()`, FAT type macros, cluster constants, and FSInfo encoding helpers.

## Invariants And Risks

- Writable mounts must mark the FAT volume dirty and must mark it clean before dropping write access during unmount or read-only remount.
- `dev->si_mountpt`, GEOM open references, `BO_NOBUFS`, device references, mount data, and the FAT lock have tightly paired setup and cleanup paths.
- BPB parsing is deliberately defensive; overflow and media-size checks prevent bogus media from creating invalid cluster arithmetic.
- The fixed FAT12/FAT16 root directory cannot grow, so root free-entry accounting is mount-time state later maintained by allocation/free macros.
- Emergency read-only remount is asynchronous and relies on busying the mount before queueing the task; pending counts are unwound in `msdosfs_remount_ro()`.
