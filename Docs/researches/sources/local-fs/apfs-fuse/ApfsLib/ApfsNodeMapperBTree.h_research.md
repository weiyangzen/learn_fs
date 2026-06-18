# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.h

This header declares `ApfsNodeMapperBTree`, an `ApfsNodeMapper` implementation backed by a `BTree`.

It stores a copied `omap_phys_t`, the B-tree itself, and a reference to `ApfsContainer` for verified block reads. Public API includes constructor, destructor, `Init()`, `Lookup()`, and `dump()` forwarding to the internal tree.

It is used for both container and volume object-map resolution. The class binds APFS logical object identity to the generic B-tree traversal code.

Dependencies are `DiskStruct.h`, `ApfsNodeMapper.h`, and `BTree.h`.
