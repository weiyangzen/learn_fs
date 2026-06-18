# File Research: sources/local-fs/xfsprogs/repair/incore.h

## Role

`incore.h` defines repair’s in-memory state structures for block ownership, free extents, duplicate extents, inode records, parent tracking, link counts, file types, and bmap cursors.

## Block State API

Declares:

- `init_bmaps`, `reset_bmaps`, `free_bmaps`.
- `lock_group`, `unlock_group`, plus AG wrappers.
- `set_bmap_ext`, `get_bmap_ext`.
- `set_rtbmap`, `get_rtbmap`.

## Block State Values

`XR_E_*` states encode repair’s view of each block:

- Unknown, free, in-use, filesystem metadata, inode block, space-map block.
- Single-source variants from btree/rmap scans.
- Duplicate/multiple-use state.
- Refcount and CoW states.
- Bad-state sentinel.

`XR_E_METADATA` is deliberately below `XR_E_INUSE` because metadata-directory files are rebuilt and their blocks must become free-space candidates later.

## Extent Trees

Defines:

- `extent_tree_node_t` for AG free/duplicate extents.
- `rt_extent_tree_node_t` for realtime duplicate extents.
- APIs for bno trees, bcnt trees, duplicate extent trees, realtime duplicate extent trees, and counts.

Bno trees are sorted by start block. Bcnt trees are sorted by length with linked-list chaining for equal-sized extents.

## Inode Records

`ino_tree_node_t` tracks a 64-inode chunk:

- Start inode.
- Free mask and sparse mask.
- Confirmed mask.
- Directory mask.
- Reflink old/new masks.
- Metadata inode mask.
- Disk nlink counters.
- Parent list or extended data.
- Optional directory filetype array.
- Per-record mutex.

`INOS_PER_IREC` and `IREC_MASK` define bit granularity.

## Inode Tree API

Declares functions to:

- Allocate and free inode records.
- Find records by AG/inode or range.
- Set inodes used/free, including allocation of new records.
- Manage uncertain inode trees.
- Add extended inode data for phases 6 and 7.
- Track parent inode numbers and link counts.
- Track directory file types.

## Inline State Helpers

The header provides inline helpers for:

- Confirmed inode state.
- Directory bit.
- Free/used bit.
- Sparse bit.
- Reflink was/is bits.
- Metadata bit.
- Reference-checked and reached bits.
- Filetype access.

Many setters take the per-record mutex because AG processing can be parallel.

## Bmap Cursor

Defines `bmap_cursor_t` and `bm_level_state_t` for validating bmap btree traversal state, including sibling pointers and first/last keys per level.

## Inobt Helpers

`inorec_get_freecount` and `inorec_set_freecount` abstract old and sparse inode btree record formats.

`xfs_rootrec_inodes_inuse` returns how many initial inodes mkfs assumes allocated, varying by metadir and rtgroup support.
