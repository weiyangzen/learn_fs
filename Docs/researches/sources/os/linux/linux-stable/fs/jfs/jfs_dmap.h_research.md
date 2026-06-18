# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.h

Defines JFS block allocation map constants, on-disk structures, conversion macros, and exported allocator APIs.

Core model:
- A `dmap` covers 8192 blocks using 256 32-bit bitmap words plus a summary tree.
- `dmapctl` pages summarize lower-level dmaps/control pages through larger trees.
- `dbmap_disk` is the on-disk aggregate descriptor with map size, free counts, allocation-group geometry, per-AG free counts, and max free buddy.
- `struct bmap` wraps the descriptor in memory with the bmap inode, mutex, active AG counters, and optional map pointer.

Important macros:
- Tree sizes/indices: `TREESIZE`, `LEAFIND`, `CTLTREESIZE`, `CTLLEAFIND`, `ROOT`, `NOFREE`.
- Geometry: `BPERDMAP`, `L2BPERDMAP`, `MAXAG`, `MAXL0SIZE`, `MAXL1SIZE`, `MAXL2SIZE`, `MAXMAPSIZE`.
- Address conversion: `BLKTODMAP`, `BLKTOL0`, `BLKTOL1`, `BLKTOCTL`, `BMAPSZTOLEV`, `BLKTOAG`, `AGTOBLK`, `BLKTOCTLLEAF`.
- Buddy helpers: `TREEMAX`, `BLKSTOL2`, `NLSTOL2BSZ`, `LITOL2BSZ`, `BUDSIZE`.

Exports:
- Mount/sync/unmount, allocate/free/reallocate, persistent-map update, AG selection, bottom-up allocation, filesystem extension/finalization, map-size calculation, and AG discard.

Risk notes:
- Header encodes on-disk layout and page geometry; changes must preserve exact structure sizes and endian fields.
- Conversion macros are dense and assume the fixed three-level dmapctl layout.
