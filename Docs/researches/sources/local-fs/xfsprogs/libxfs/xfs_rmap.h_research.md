# File Research: sources/local-fs/xfsprogs/libxfs/xfs_rmap.h

Public interface for reverse mapping operations. It defines owner-info helpers, rmap offset packing, rmap intent types, query APIs, owner-match result structures, owner constants, and optional live hook declarations.

Key helpers:
- `xfs_rmap_ino_bmbt_owner` and `xfs_rmap_ino_owner` build owner-info records for inode bmbt and data/attr fork mappings.
- `xfs_rmap_should_skip_owner_update` tests for the null-owner sentinel.
- `xfs_rmap_irec_offset_pack` stores file offset plus attr fork, bmbt, and unwritten bits into the on-disk offset field.
- `xfs_rmap_irec_offset_unpack` validates and decodes that packed field.
- `xfs_owner_info_pack` and `xfs_owner_info_unpack` convert between owner-info flags and rmap flags.

Exported operations:
- Direct AG rmap APIs: `xfs_rmap_alloc`, `xfs_rmap_free`, lookups, insert, get record.
- Query APIs: `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`.
- Deferred update APIs from bmap/allocation paths: map, unmap, convert, alloc extent, free extent.
- Intent finish APIs: `xfs_rmap_finish_one` and `__xfs_rmap_finish_intent`.
- Validation and comparison: `xfs_rmap_btrec_to_irec`, AG/realtime record checks, `xfs_rmap_compare`.
- Ownership checks: `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, and `struct xfs_rmap_matches`.

Intent model:
- `enum xfs_rmap_intent_type` distinguishes normal/shared map, normal/shared unmap, normal/shared conversion, metadata allocation, and metadata free.
- `struct xfs_rmap_intent` stores operation type, fork, owner, bmbt mapping, group, and realtime flag.

Constants:
- Declares common owner-info singletons for skip, any owner, filesystem, log, AG metadata, inode btrees, inode chunks, refcountbt, and CoW staging.

Optional hooks:
- Under `CONFIG_XFS_LIVE_HOOKS`, exposes hook setup/add/delete and enable/disable functions for rmap update observation.
