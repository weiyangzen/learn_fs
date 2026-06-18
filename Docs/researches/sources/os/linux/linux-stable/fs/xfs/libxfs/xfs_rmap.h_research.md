# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.h

## Scope

Public reverse-map interface and inline helpers for owner-info construction, rmap offset packing/unpacking, deferred intent structures, query callbacks, owner-count reporting, live hook declarations, and well-known metadata owner constants.

## APIs And Types

- Owner helpers: `xfs_rmap_ino_bmbt_owner`, `xfs_rmap_ino_owner`, `xfs_rmap_should_skip_owner_update`, `xfs_owner_info_pack`, `xfs_owner_info_unpack`.
- Offset helpers: `xfs_rmap_irec_offset_pack`, `xfs_rmap_irec_offset_unpack`.
- Primitive declarations: `xfs_rmap_alloc`, `xfs_rmap_free`, lookups, insert, get-rec, range/all queries.
- Deferred intent model: `enum xfs_rmap_intent_type`, `XFS_RMAP_INTENT_STRINGS`, and `struct xfs_rmap_intent`.
- Bmap-driven update APIs: map, unmap, convert, alloc/free metadata extent, finish-one replay.
- Query/comparison APIs: `xfs_rmap_lookup_le_range`, `xfs_rmap_compare`, record conversion/checking, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`, `xfs_rmap_map_raw`.
- Owner-count result type: `struct xfs_rmap_matches`.
- Live update hook structures and functions when configured.

## Constants

- Declares well-known `xfs_owner_info` constants for skip update, any owner, filesystem, log, AG, inode btree, inode chunk, refcount btree, and CoW owners.
- `XFS_RMAP_INTENT_STRINGS` names deferred rmap operations for tracing/logging.

## Dependencies

- Depends on XFS owner-info flags, rmap record format flags, btree cursor APIs, transactions, inode fork ids, bmap records, groups, realtime groups, and hook infrastructure.

## Invariants And Risks

- Offset packing masks with `XFS_RMAP_OFF_MASK`; unexpected high bits in on-disk offset fields are corruption.
- `xfs_rmap_should_skip_owner_update` treats null owner as a sentinel, not a real reverse-map owner.
- `xfs_owner_info_pack` intentionally preserves only attr-fork and bmbt-block flags; unwritten state is supplied separately by bmap state.
