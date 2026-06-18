# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_rmap.h

Public interface and inline helpers for reverse mapping operations.

Key contents:
- Owner-info constructors for inode bmbt owners and inode data/attr fork owners.
- `xfs_rmap_should_skip_owner_update` sentinel check.
- Inline pack/unpack helpers for rmap offset fields, including attr fork, bmbt block, and unwritten flags.
- `xfs_owner_info_pack/unpack` bridging owner-info flags and rmap record flags.
- Declares direct rmap allocation/free APIs and lower-level lookup/insert/get/query functions.
- Defines deferred rmap intent types and `struct xfs_rmap_intent`.
- Declares bmap-driven APIs for map, unmap, convert, metadata alloc, and metadata free.
- Declares owner-count result structure `xfs_rmap_matches`.
- Declares constants for common metadata owners such as FS, log, AG, inode btree, inode chunks, refcount btree, and CoW.
- Exposes optional live hook setup and registration APIs.

Design notes:
- The packed offset format treats unwritten as a record attribute, while attr fork and bmbt are key-significant.
- The deferred intent structure stores a full bmap record plus owner/fork metadata so updates can be replayed later.
