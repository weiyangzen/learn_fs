# File Research: sources/os/linux/linux/fs/xfs/scrub/rtrmap.c

## Purpose
Scrubs realtime reverse mapping btrees. It validates realtime rmap records, detects illegal overlaps and mergeable records, and cross-references realtime ownership with rtbitmap and rtrefcount metadata.

## Major Components
- `xchk_setup_rtrmapbt`: repair-aware setup, rtgroup initialization, live rmap inode install, and rtgroup locking.
- `struct xchk_rtrmap`: previous and furthest-overlap tracking.
- Record checks:
  - `xchk_rtrmapbt_rec`
  - `xchk_rtrmapbt_check_overlapping`
  - `xchk_rtrmapbt_check_mergeable`
  - `xchk_rtrmapbt_xref`
  - `xchk_rtrmapbt_xref_rtrefc`
- Whole-tree scrub: `xchk_rtrmapbt`.
- Xref helpers:
  - `xchk_xref_has_no_rt_owner`
  - `xchk_xref_has_rt_owner`
  - `xchk_xref_is_only_rt_owned_by`

## Control Flow and Invariants
The scrubber validates metadata inode forks, derives the rmap inode owner info, then walks the rtrmapbt. Records must:
- Decode cleanly and pass `xfs_rtrmap_check_irec`.
- Not overlap unless realtime reflink permits sharing and records are not unwritten.
- Not be mergeable with adjacent records.
- Refer to used realtime space.
- If shared, correspond to shareable data fork mappings.

## Dependencies and Integration
Uses realtime bitmap xref for used/free validation and rtrefcountbt xref for shared-state validation. Other realtime scrubbers call this file’s xref helpers to assert ownership or absence of ownership.

## Risk and Edge Cases
- Realtime rmap records are simpler than AG rmap records because they describe realtime data fork extents, but live consistency still depends on rtgroup locking.
- In the CoW branch, `xchk_rtrmapbt_xref` calls the AG CoW xref helper rather than the realtime-specific helper; this is a notable integration detail to verify against surrounding code expectations.
