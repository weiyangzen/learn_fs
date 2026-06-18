# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/fs.h

## Purpose
Defines the core on-disk and in-memory layout contract for FreeBSD FFS/UFS: superblock locations, filesystem geometry, cylinder group metadata, allocation/addressing macros, feature flags, metadata checksum flags, snapshot sentinel blocks, soft-update journal record formats, and UFS suspension ioctls.

## Key Contents
- Superblock constants:
  - `SBLOCK_FLOPPY`, `SBLOCK_UFS1`, `SBLOCK_UFS2`, `SBLOCK_PIGGY`
  - `SBLOCKSEARCH`
  - `SBLOCKSIZE`
  - `UFS_STDSB`
- Superblock read/validation flags:
  - `UFS_NOHASHFAIL`, `UFS_NOWARNFAIL`, `UFS_NOMSG`, `UFS_NOCSUM`, `UFS_FSRONLY`, `UFS_ALTSBLK`
- Filesystem sizing/layout constants:
  - `MAXFRAG`, `MINBSIZE`, `MAXMNTLEN`, `MAXVOLLEN`, `FS_MAXCONTIG`, `MINFREE`, `FSMAXSNAP`
- Snapshot special block values:
  - `BLK_NOCOPY`
  - `BLK_SNAP`
- fsck command protocol:
  - `FFS_ADJ_REFCNT` through `FFS_ADJ_DEPTH`
  - `struct fsck_cmd`
  - `struct fsrecovery`
- Summary structures:
  - `struct csum`
  - `struct csum_total`
  - `struct fs_summary_info`
- Main FFS superblock:
  - `struct fs`
  - Preserves historical UFS1 fields, modern UFS2 fields, mount metadata, summary pointers, snapshot inode list, checksum state, flags, and geometry constants.
  - Compile-time assertion expects `sizeof(struct fs) == 1376`.
- Filesystem magic and format constants:
  - `FS_UFS1_MAGIC`, `FS_UFS2_MAGIC`, `FS_BAD_MAGIC`
  - `FS_42INODEFMT`, `FS_44INODEFMT`
- Filesystem feature flags:
  - `FS_UNCLEAN`, `FS_DOSOFTDEP`, `FS_NEEDSFSCK`, `FS_SUJ`, `FS_ACLS`, `FS_MULTILABEL`, `FS_GJOURNAL`, `FS_NFS4ACLS`, `FS_METACKHASH`, `FS_TRIM`
  - Future/unsupported feature bits are defined and cleared at mount via `FS_SUPPORTED`.
- Metadata checksum flags:
  - `CK_SUPERBLOCK`, `CK_CYLGRP`, `CK_INODE`, `CK_INDIR`, `CK_DIR`
- Buffer extended flags for metadata identity:
  - `BX_SUPERBLOCK`, `BX_CYLGRP`, `BX_INODE`, `BX_INDIR`, `BX_DIR`
- Cylinder group layout:
  - `CGSIZE(fs)`
  - `struct cg`
  - Access macros: `cg_inosused`, `cg_blksfree`, `cg_clustersfree`, `cg_clustersum`
- Address translation macros:
  - `fsbtodb`, `dbtofsb`
  - `cgbase`, `cgdata`, `cgmeta`, `cgdmin`, `cgimin`, `cgsblock`, `cgtod`, `cgstart`
  - `ino_to_cg`, `ino_to_fsba`, `ino_to_fsbo`
  - `dtog`, `dtogd`
- Block/fragments arithmetic:
  - `blkoff`, `fragoff`, `lblktosize`, `lfragtosize`, `lblkno`, `numfrags`, `blkroundup`, `fragroundup`, `fragstoblks`, `blkstofrags`, `fragnum`, `blknum`
- File block size helpers:
  - `blksize(fs, ip, lbn)`
  - `sblksize(fs, size, lbn)`
- Indirect block helpers:
  - `NINDIR(fs)`
  - `lbn_level()`
  - `lbn_offset()`
- Inode block helpers:
  - `INOPB(fs)`
  - `INOPF(fs)`
- Soft-update journal record definitions:
  - Journal op types: `JOP_ADDREF`, `JOP_REMREF`, `JOP_NEWBLK`, `JOP_FREEBLK`, `JOP_MVREF`, `JOP_TRUNC`, `JOP_SYNC`
  - `struct jsegrec`, `jrefrec`, `jmvrec`, `jblkrec`, `jtrncrec`
  - `union jrec`
  - Compile-time assertions keep each journal record at `JREC_SIZE == 32`.
- UFS write suspension ioctls:
  - `UFSSUSPEND`
  - `UFSRESUME`

## Interactions
- Included by UFS/FFS implementation files that need filesystem geometry, metadata layout, journal record formats, and feature flags.
- Depends on `ufs/ufs/dinode.h` for address/time/inode constants.
- `ufs_bmap.c` relies on block pointer semantics and indirect addressing.
- `ufs_gjournal.c` uses cylinder group and superblock counters.
- Soft-update journaling code uses the `jrec` formats declared here.
