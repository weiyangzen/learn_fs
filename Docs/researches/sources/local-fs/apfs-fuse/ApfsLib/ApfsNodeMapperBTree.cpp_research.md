# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapperBTree.cpp

This file implements object-map lookup using an APFS OMAP B-tree. `Init()` reads and verifies the `omap_phys_t` block at the OMAP OID, copies its header, validates type intent, and initializes an internal `BTree` using `om_tree_oid`.

`Lookup()` constructs an `omap_key_t` with requested OID/XID and searches the OMAP tree using a comparator that orders by OID then XID. It requests non-exact lookup, then verifies the returned OID matches, allowing the B-tree search to return the nearest mapping.

Successful lookups populate `omap_res_t` with returned OID, XID, flags, object size, and physical address from `omap_val_t`.

Notable risk: `CompareOMapKey()` asserts `ekey_len == sizeof(omap_val_t)`, but `ekey` is interpreted as `omap_key_t`; this looks like a copy/paste assert bug and can mislead debugging.
