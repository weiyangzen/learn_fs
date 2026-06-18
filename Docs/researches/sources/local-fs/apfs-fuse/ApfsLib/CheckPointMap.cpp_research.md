# File Research: sources/local-fs/apfs-fuse/ApfsLib/CheckPointMap.cpp

`CheckPointMap` implements `ApfsNodeMapper` for APFS checkpoint maps. `Init()` reads a contiguous checkpoint-map block range from the container, verifies each header block, and ensures object type is `OBJECT_TYPE_CHECKPOINT_MAP`.

`Lookup()` linearly scans all stored checkpoint map blocks and entries for a matching OID, ignoring the requested XID. It returns OID, checkpoint XID, size, and physical address in `omap_res_t`.

`dump()` passes the stored checkpoint map data to `BlockDumper`.

This mapper is used early during container initialization before the normal OMAP B-tree can be used, especially to resolve spaceman and free-queue objects.
