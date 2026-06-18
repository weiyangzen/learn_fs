# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_fs.h

## Role

Defines the UFS on-disk superblock and cylinder-group format, constants, clean-state/version values, allocation geometry macros, bitmap helpers, block/inode address translation, and lockfs-aware inode lock acquisition macros.

## Key Disk Structures

- `struct csum` summarizes directories, free blocks, free inodes, and free fragments.
- `struct fs` is the UFS superblock: block geometry, cylinder group layout, allocation parameters, clean state, mount path, summary info, rotation tables, version/log metadata, reclaim flags, masks, and magic.
- `struct cg` is the modern cylinder-group block containing summary info, rotor positions, fragment summaries, and offsets to variable-length maps.
- `struct ocg` preserves compatibility with old cylinder-group layout.

## Constants and State

Defines boot/superblock offsets and sizes, root/lost+found inode numbers, maximum UFS file offset bits, `FS_MAGIC`, `MTB_UFS_MAGIC`, `FSOKAY`, clean states (`FSACTIVE`, `FSCLEAN`, `FSSTABLE`, `FSBAD`, `FSSUSPEND`, `FSLOG`, `FSFIX`), largefile flag, reclaim states, log roll states, summary-info validity, optimization modes, and rotational table formats.

## Geometry and Access Macros

Provides conversion and location macros:
- Superblock/cylinder/inode/data locations: `cgbase`, `cgstart`, `cgsblock`, `cgtod`, `cgimin`, `cgdmin`.
- Inode mapping: `itoo`, `itog`, `itod`.
- Block/cylinder mapping: `dtog`, `dtogd`, `blkmap`, `cbtocylno`, `cbtorpos`.
- Offset/block math: `blkoff`, `fragoff`, `lblkno`, `numfrags`, `blkroundup`, `fragroundup`, `fragstoblks`, `blkstofrags`, `fragnum`, `blknum`.
- Size helpers: `blksize`, `dblksize`, `NSPB`, `NSPF`, `INOPB`, `INOPF`, `NINDIR`.
- Bitmap helpers: `setbit`, `clrbit`, `isset`, `isclr`.

## Lockfs Interaction

`ufs_tryirwlock()` and `ufs_tryirwlock_trans()` use `rw_tryenter()` to avoid deadlocks when lockfs soft-lock (`SLOCK`) conflicts with vnode operation lock ordering. The transaction variant unwinds transaction and lockfs state before retrying.

## Risk Notes

This file is core disk-format ABI. Endian-dependent superblock field ordering is intentionally preserved for SVR4 compatibility. Any geometry macro change can corrupt allocation, fsck interpretation, or bootloader compatibility.
