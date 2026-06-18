# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/dirhash.h

## Purpose
Declares the optional UFS directory hash cache used to speed up operations on large directories and maintain free-space hints.

## Key Contents
- Hash slot sentinels:
  - `DIRHASH_EMPTY`
  - `DIRHASH_DEL`
- Alignment/stat constants:
  - `DIRALIGN`
  - `DH_NFSTATS`
- Recycling score policy:
  - `DH_SCOREINIT`
  - `DH_SCOREMAX`
- Two-level hash table geometry:
  - `DH_BLKOFFSHIFT`
  - `DH_NBLKOFF`
  - `DH_BLKOFFMASK`
  - `DH_ENTRY(dh, slot)`
- `struct dirhash`:
  - `sx` lock and refcount.
  - Two-level hash array of directory offsets.
  - Hash size/usage/memory counters.
  - Per-directory-block free-space summaries.
  - `dh_firstfree[]` index by free-space bucket.
  - Sequential lookup hint `dh_seqoff`.
  - LRU/LFU hybrid score and global list linkage.
- Function declarations:
  - Lifecycle: `ufsdirhash_init`, `ufsdirhash_uninit`, `ufsdirhash_free`
  - Build/lookup: `ufsdirhash_build`, `ufsdirhash_lookup`
  - Free-space helpers: `ufsdirhash_findfree`, `ufsdirhash_enduseful`
  - Mutation hooks: `ufsdirhash_newblk`, `ufsdirhash_add`, `ufsdirhash_remove`, `ufsdirhash_move`, `ufsdirhash_dirtrunc`
  - Debug checking: `ufsdirhash_checkblock`

## Interactions
- Implemented in `ufs_dirhash.c`.
- Referenced by `struct inode` as `i_dirhash`.
- Used by directory lookup and mutation paths to avoid linear scans on large directories.
