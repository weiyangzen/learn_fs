# File Research: sources/os/linux/linux/fs/jfs/jfs_dmap.h

## Purpose
Defines JFS block allocation-map constants, dmap/dmapctl/global descriptor structures, conversion macros, and exported allocator interfaces.

## Constants
- Dmap geometry: `TREESIZE`, `LEAFIND`, `LPERDMAP`, `DBWORD`, `BUDMIN`, `BPERDMAP`, `L2BPERDMAP`.
- Dmapctl geometry: `CTLTREESIZE`, `CTLLEAFIND`, `LPERCTL`, `L2LPERCTL`.
- Map limits: `MAXAG`, `L2MAXAG`, `L2MAXL0SIZE`, `L2MAXL1SIZE`, `L2MAXL2SIZE`, `MAXMAPSIZE`.
- `ROOT` identifies the root summary-tree index.
- `NOFREE` is `-1`, used when a subtree has no free blocks.

## Conversion Helpers
- `TREEMAX()` returns the max value of four sibling tree entries.
- `BLKTODMAP()`, `BLKTOL0()`, `BLKTOL1()`, and `BLKTOCTL()` translate aggregate block numbers to bmap file logical blocks.
- `BMAPSZTOLEV()` maps aggregate size to top dmapctl level.
- `BLKTOAG()` and `AGTOBLK()` convert between block numbers and allocation groups.
- `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BLKTOCTLLEAF`, and `BUDSIZE` support buddy sizing and tree indexing.

## Structures
- `struct dmaptree`: fixed metadata plus 341-entry dmap summary tree.
- `struct dmap`: one 4096-byte dmap page covering 8192 blocks, with free counts, start block, summary tree, working bitmap, and persistent bitmap.
- `struct dmapctl`: 4096-byte control-page summary tree for higher-level dmap coverage.
- `union dmtree`: overlays dmap and dmapctl tree metadata for generic tree routines.
- `struct dbmap_disk`: on-disk global allocation-map descriptor with aggregate counts, AG configuration/free counts, and max free buddy.
- `struct dbmap`: endian-native in-memory counterpart.
- `struct bmap`: runtime descriptor containing `dbmap`, bmap inode pointer, global bmap mutex, per-AG active-writer counters, and `db_DBmap`.

## Exported API
- Lifecycle/sync: `dbMount()`, `dbUnmount()`, `dbSync()`, `dbFinalizeBmap()`.
- Allocation/free: `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `dbAllocBottomUp()`.
- Persistent bitmap and resize: `dbUpdatePMap()`, `dbExtendFS()`, `dbMapFileSizeToMapSize()`.
- Policy and discard: `dbNextAG()`, `dbDiscardAG()`.

## Dependencies
- Includes `jfs_txnmgr.h` because persistent-map updates need transaction blocks.
- Implemented primarily by `jfs_dmap.c`.
