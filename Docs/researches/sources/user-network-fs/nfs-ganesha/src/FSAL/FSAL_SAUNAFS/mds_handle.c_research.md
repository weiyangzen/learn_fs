# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_handle.c

This file implements pNFS object-handle operations for SaunaFS MDS behavior: layoutget, layoutreturn, and layoutcommit. It encodes file layouts that point clients at DS handles and commits client-reported size/mtime changes back to SaunaFS metadata.

The main functions are `layoutget`, `layoutreturn`, `isOffsetChangedByClient`, `hasRecentModificationTime`, `layoutcommit`, and `handleOperationsPnfs`. `layoutget` validates the layout type, builds a `pnfs_deviceid` from FSAL id/export id/inode, encodes a `DSWire` inode payload with `FSAL_encode_file_layout`, uses `SFSCHUNKSIZE` as layout utility, sets `return_on_close`, and marks the response as the last segment. `layoutreturn` validates type and otherwise accepts returns without extra state. `layoutcommit` fetches current attributes, conditionally sets size when `last_write + 1` exceeds current size, conditionally sets mtime only if the client time is newer, calls `saunafs_setattr`, and marks commit done.

State is minimal. Layout identity is encoded through inode/export id; no per-layout allocation is stored in this file. Persistent effects happen only in `layoutcommit` through size and mtime setattr.

Dependencies include `pnfs_utils`, `context_wrap`, private SaunaFS types, XDR encoding, and Ganesha `op_ctx`. Integration point is `handleOperationsPnfs`, called during object ops initialization.

Risks include broad layouts with no range-specific tracking, no verification of returned layout body, no stateid-specific checks in these functions, and layoutcommit performing setattr even when mask remains zero. Test signals should cover unsupported layout types, encoded DS wire handle size/content, return-on-close behavior, size growth on layoutcommit, mtime conflict rules, no-op layoutcommit, getattr/setattr failure mapping, and pNFS client interoperability.
