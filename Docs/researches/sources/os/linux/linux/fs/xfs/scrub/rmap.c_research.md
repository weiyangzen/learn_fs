# File Research: sources/os/linux/linux/fs/xfs/scrub/rmap.c

## Purpose
Scrubs per-AG reverse mapping btrees. It validates record structure, detects illegal overlaps and mergeable records, cross-references ownership against allocation/refcount/inode metadata, and compares AG metadata bitmaps against rmap records.

## Major Components
- `xchk_setup_ag_rmapbt`: repair-aware setup and intent drain gate.
- `struct xchk_rmap`: tracks overlap/previous records and metadata-owned bitmaps.
- Record checks:
  - `xchk_rmapbt_rec`
  - `xchk_rmapbt_check_unwritten_in_keyflags`
  - `xchk_rmapbt_check_overlapping`
  - `xchk_rmapbt_check_mergeable`
- Metadata bitmap construction:
  - `xchk_rmapbt_walk_ag_metadata`
  - `xchk_rmapbt_mark_bitmap`
  - `xchk_rmapbt_check_bitmaps`
- Whole-tree scrub: `xchk_rmapbt`.
- Xref helpers:
  - `xchk_xref_is_only_owned_by`
  - `xchk_xref_is_not_owned_by`
  - `xchk_xref_has_no_owner`

## Control Flow and Invariants
Before walking the rmapbt, the scrubber builds bitmaps for AG-owned metadata:
- AG headers and AGFL;
- internal log if in this AG;
- free-space btree blocks;
- inode btree blocks and finobt;
- refcountbt blocks if reflink is enabled.

During rmapbt traversal, records are checked for:
- valid conversion and `xfs_rmap_check_irec`;
- stale unwritten bits in node keys, marked as preen;
- adjacent records that could have been merged;
- illegal overlap unless both records are shareable data fork extents;
- consistency with used/free space, inode chunk ownership, CoW/refcount state.

Metadata rmap records clear corresponding bitmap regions. After traversal, any remaining set bitmap bits indicate missing rmap records.

## Dependencies and Integration
Uses `xagb_bitmap`, allocation btrees, inode btrees, refcountbt, AGFL walking, and generic scrub btree traversal. Its xref helpers are used broadly by other metadata scrubbers.

## Risk and Edge Cases
- Bitmap cross-reference is disabled if metadata walking fails, to avoid false xref corruptions.
- Shared overlap is allowed only for reflink-capable data fork mappings that are neither bmbt blocks, attr fork, nor unwritten.
- The preen path detects historical unwritten key contamination without marking corruption.
