# File Research: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.h

This header declares `CheckPointMap`, an `ApfsNodeMapper` backed by in-memory checkpoint-map block data.

It stores an `ApfsContainer&`, a vector of checkpoint-map bytes, the root checkpoint-map OID, and block size.

Public API includes construction, destruction, `Init(root_oid, blk_count)`, `Lookup()`, and diagnostic `dump()`.

It is intentionally simple and linear because checkpoint maps are small bootstrap metadata compared with APFS object-map B-trees.
