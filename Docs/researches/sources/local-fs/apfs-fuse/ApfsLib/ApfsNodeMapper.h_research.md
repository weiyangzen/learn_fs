# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsNodeMapper.h

This header defines `omap_res_t`, the normalized result of APFS object-map resolution: OID, XID, flags, object size, and physical address.

`ApfsNodeMapper` is an abstract interface with one operation, `Lookup(omap_res_t&, oid_t, xid_t)`. B-tree code depends on this interface to convert logical APFS object IDs into physical block addresses.

The interface keeps checkpoint maps and B-tree object maps interchangeable from the B-tree reader’s perspective.

It depends only on `ApfsTypes.h`, making it a small foundational type boundary.
