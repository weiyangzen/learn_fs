# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_fork.h

## Role

This header defines the incore inode fork structure and declares fork formatting, flushing, extent tree, local data, CoW fork, and extent count helper APIs.

## Main Data Structure

`struct xfs_ifork` stores:

- `if_bytes` for bytes used by local data or incore extent records
- `if_broot` and `if_broot_bytes` for incore bmap btree roots
- `if_seq` modification counter
- `if_height` and `if_data` for the incore extent tree or local data
- `if_nextents` on-disk extent count
- `if_format` dinode fork format
- `if_needextents` lazy-load flag for btree extent caches

## Extent Count Planning

The header defines worst-case extent count deltas for common operations:

- adding an extent without splitting
- punching a hole
- attr manipulation including remote xattr blocks
- writing into unwritten extents
- ending CoW
- reflink mapping swaps

`xfs_iext_max_nextents` returns fork-specific small or large extent counter limits.

## Fork Helpers

Inline helpers include:

- `XFS_IFORK_MAXEXT` for inline extent capacity
- `xfs_ifork_has_extents`
- `xfs_ifork_nextents`
- `xfs_ifork_format`
- `xfs_dfork_data_extents`
- `xfs_dfork_attr_extents`
- `xfs_dfork_nextents`
- `xfs_need_iread_extents`

The large extent counter helpers choose between old and new dinode counter fields.

## Extent Cursor APIs

The header declares all incore extent tree operations and provides convenience wrappers:

- `xfs_iext_next_extent`
- `xfs_iext_prev_extent`
- `xfs_iext_peek_next_extent`
- `xfs_iext_peek_prev_extent`
- `for_each_xfs_iext`

## Dependencies

This header binds together inode fork state, dinode fork formats, bmap records, btree roots, transaction logging, and extent cursor iteration. It is included by most inode mapping and fork manipulation code.

## Research Notes

`if_bytes` has different meanings depending on fork format, so callers must pair it with `if_format`. The `if_needextents` acquire-load contract is subtle: readers depend on seeing a valid format after observing that lazy extent loading is needed.
