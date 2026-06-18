# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfsmount.h

## Purpose

`msdosfsmount.h` defines the in-kernel mount control block, mount arguments, flags, locking macros, and block/cluster conversion helpers for FreeBSD msdosfs. It is the shared structural contract between msdosfs VFS operations, vnode operations, FAT code, denode code, and user-facing mount argument translation.

## Key Structures

`struct msdosfsmount` stores all per-mount state:

- VFS and device integration: `pm_mountp`, GEOM consumer `pm_cp`, device buffer object `pm_bo`, mounted device vnode `pm_devvp`, original device vnode `pm_odevvp`, and character device `pm_dev`.
- Ownership and permission synthesis: `pm_uid`, `pm_gid`, `pm_mask`, and `pm_dirmask`.
- BPB and filesystem geometry: `pm_bpb`, sector/block ratios, FAT sector counts, FAT start block, root directory block or FAT32 cluster, fixed root directory size, first data cluster, max cluster, cluster/block shift values, bytes per cluster, FAT block size, FAT size, FAT mask, FAT32 FSInfo block, current FAT, and root directory free-slot count.
- Allocation state: `pm_freeclustercount`, `pm_nxtfree`, `pm_fatmult`, `pm_fatdiv`, and `pm_inusemap`.
- Runtime flags and services: `pm_flags`, iconv handles for local/Unicode/DOS conversions, `pm_fatlock`, and `pm_rw2ro_task` for emergency read-only remount.

`struct msdosfs_fileno` maps a 64-bit file number to a 32-bit number in a red-black tree node. This header declares the structure but the behavior lives elsewhere.

`struct msdosfs_args` is the legacy kernel mount argument layout consumed by `msdosfs_cmount()`: device path, export args, uid/gid, file mask, flags, old unused Unicode table storage, charset names, and directory mask.

## Macros And Helpers

The header aliases BPB fields (`pm_BytesPerSec`, `pm_ResSectors`, `pm_FATs`, and others) into the embedded BPB. It defines `VFSTOMSDOSFS()` for retrieving mount data, `FATOFS()` for byte offsets into the FAT, `N_INUSEBITS` for allocation bitmap sizing, and multiple conversions among file offsets, logical cluster numbers, device block numbers, and FAT root directory locations.

Important conversion helpers include:

- `de_cluster()`, `de_clcount()`, `de_blk()`, `de_cn2off()`, and `de_bn2off()` for translating file offsets and cluster/block units.
- `cntobn()` for mapping a data cluster number to a filesystem-relative device block.
- `roottobn()` and `detobn()` for fixed root directory and ordinary directory entry block mapping.
- `bptoep()` for locating a `struct direntry` inside a buffer by directory offset.

The root directory accounting macros `rootde_alloced()` and `rootde_freed()` update `pm_rootdirfree` only for fixed FAT12/FAT16 root directories. The lock macros wrap `pm_fatlock` through `lockmgr()`.

## Flags

Mount option flags include `MSDOSFSMNT_SHORTNAME`, `MSDOSFSMNT_LONGNAME`, `MSDOSFSMNT_NOWIN95`, and `MSDOSFSMNT_KICONV`. Runtime/internal flags include `MSDOSFSMNT_RONLY`, `MSDOSFSMNT_WAITONFAT`, `MSDOSFS_FATMIRROR`, `MSDOSFS_FSIMOD`, and `MSDOSFS_ERR_RO`.

## Dependencies

The header depends on kernel lock, task, tree, mount/vnode/device types, FAT BPB definitions, and directory entry/cluster constants from the rest of msdosfs. It exposes `msdosfs_integrity_error()` to kernel code.

## Invariants And Risks

- Shift and mask conversion macros assume power-of-two sector and cluster sizes validated at mount time.
- `pm_rootdirblk` means a block number for FAT12/16 but a root cluster for FAT32; callers must use FAT type checks correctly.
- `pm_fatlock` protects FAT allocation state and must be held for allocation bitmap/FAT mutations.
- Mount option flags and internal runtime flags share `pm_flags`, so option-mask use must avoid clobbering runtime bits.
