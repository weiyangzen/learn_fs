# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/msdosfsmount.h

## Summary
Defines msdosfs mount arguments, mount option flags, the in-kernel/makefs mount control block, FAT geometry macros, directory-entry address helpers, and VFS prototypes. It is the central shared header for msdosfs mount state and sector/cluster/block conversions.

## Main Responsibilities
- Define `struct msdosfs_args` for mount arguments, including versioned extensions for directory mask and GMT offset.
- Define user-visible and internal mount flags: short names, long names, ignoring Win95 entries, GEMDOS mode, versioned args, UTF-8 names, read-only, synchronous FAT updates, and FAT mirroring.
- Declare msdosfs malloc types under `_KERNEL`.
- Define `struct msdosfsmount`, holding mount/device identity, uid/gid/masks, timezone offset, BPB copy, FAT/root/cluster geometry, free-space state, FAT type parameters, current FAT, allocation bitmap, and flags.
- Provide FAT byte-offset macro `FATOFS()`.
- Provide mount conversion macro `VFSTOMSDOSFS()`.
- Define allocation bitmap unit size `N_INUSEBITS`.
- Alias BPB fields through `pm_*` macros.
- Convert between directory offsets, cluster numbers, filesystem sectors, kernel block numbers, and file offsets.
- Declare msdosfs VFS lifecycle functions and `VFS_PROTOS(msdosfs)`.

## Key Interfaces
- `struct msdosfs_args`.
- `struct msdosfsmount`.
- Mount flags `MSDOSFSMNT_*` and `MSDOSFS_FATMIRROR`.
- Conversion macros: `FATOFS`, `bptoep`, `de_bn2cn`, `de_cn2bn`, `de_bn2kb`, `de_kb2bn`, `de_cluster`, `de_clcount`, `de_blk`, `de_cn2off`, `de_bn2off`, `cntobn`, `roottobn`, and `detobn`.
- Prototypes: `msdosfs_init`, `msdosfs_reinit`, `msdosfs_done`, and kernel VFS prototypes.

## Risks
Many macros assume power-of-two sector and cluster sizes and valid shift relationships initialized by mount validation. Incorrect `pm_*` geometry can turn simple macros into invalid block numbers or offsets. `detobn()` maps non-root directory offsets only to the directory's starting cluster, so callers must already use FAT-chain mapping when offsets may span later clusters. The mount argument structure preserves compatibility fields, so version handling in callers must stay aligned with this header.
