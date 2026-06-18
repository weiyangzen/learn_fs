# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsContainer.h

This header defines the `ApfsContainer` class, the main object representing an APFS container over one or two `Device` instances. It exposes initialization, volume lookup, volume-info lookup, block reads, checksum-verified header reads, block size/count/free count accessors, volume key lookup, password hint lookup, and diagnostic dumping.

Internally it stores main and tier2 device pointers plus partition offsets/lengths, the current `nx_superblock_t`, a `CheckPointMap`, a B-tree-backed container OMAP, spaceman data, free queue trees, and `KeyManager`.

The constructor accepts raw non-owning device pointers. Volumes returned by `GetVolume()` are heap allocated and caller-owned. This mirrors the older code style used throughout the project.

It imports `BTree.h`, `DiskStruct.h`, `Device.h`, `CheckPointMap.h`, `ApfsNodeMapperBTree.h`, and `KeyMgmt.h`, making it the central aggregation point for container-level APFS parsing.
