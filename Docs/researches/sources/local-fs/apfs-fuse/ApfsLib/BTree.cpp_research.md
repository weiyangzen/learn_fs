# File Research: sources/local-fs/apfs-fuse/ApfsLib/BTree.cpp

This file implements the generic APFS B-tree reader. It supports fixed-size and variable-size key/value nodes, root and non-root node layout, object-map-backed node resolution, lookup, lower/upper-bound style searches, iterators, node caching, and recursive diagnostic dumping.

`BTreeNodeFix` reads `kvoff_t` entries and uses fixed key/value sizes from root `btree_info_t`. `BTreeNodeVar` reads `kvloc_t` entries with per-entry key/value lengths. Both return borrowed pointers into the node’s owned block buffer, while `BTreeEntry` keeps a shared node reference so pointers remain valid.

`BTree::Init()` loads the root, extracts `btree_info_t`, and stores OID/XID/mapper. `Lookup()` descends internal nodes using `FindBin(..., LE)`, resolves child OIDs including hashed-node child offsets, then searches leaves using exact or less/equal mode. `GetIterator()` and `GetIteratorBegin()` provide ordered traversal.

`GetNode()` maps OIDs through an optional `ApfsNodeMapper`, reads via `ApfsVolume` when volume encryption may apply, otherwise reads verified container blocks. With `BTREE_USE_MAP`, it caches up to 8192 nodes and prunes shared_ptrs with use count 1.

Notable risks: binary search assumes comparator return is exactly -1/0/1 and indexes `resstr[rc + 1]` in debug mode. Node validation is mostly checksum-based; malformed table offsets can still drive pointer arithmetic.
