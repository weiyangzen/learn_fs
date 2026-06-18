# File Research: sources/os/linux/linux/fs/xfs/scrub/rtrefcount.c

## Purpose
Scrubs realtime refcount btrees. It mirrors AG refcount scrub logic but operates on rtgroup-relative block numbers and realtime metadata inode btrees.

## Major Components
- `xchk_setup_rtrefcountbt`: repair-aware setup, rtgroup initialization, live refcount inode install, and rtgroup locking.
- Fragment-based rmap verification:
  - `xchk_rtrefcountbt_rmap_check`
  - `xchk_rtrefcountbt_process_rmap_fragments`
  - `xchk_rtrefcountbt_xref_rmap`
- Record checks:
  - `xchk_rtrefcountbt_rec`
  - `xchk_rtrefcountbt_check_mergeable`
  - `xchk_rtrefcountbt_xref_gaps`
- Whole-tree scrub: `xchk_rtrefcountbt`.
- Xref helpers:
  - `xchk_xref_is_rt_cow_staging`
  - `xchk_xref_is_not_rt_shared`
  - `xchk_xref_is_not_rt_cow_staging`

## Control Flow and Invariants
The scrubber first validates metadata inode forks, then walks the rtrefcountbt. Each record must:
- Pass `xfs_rtrefcount_check_irec`.
- Start and end on full realtime extent boundaries.
- Keep shared records before CoW records.
- Not be mergeable with adjacent records.
- Cross-reference with used realtime space and rtrmapbt ownership.

It also compares counted rtrefcountbt blocks against data-device rmap records for the rtrefcount metadata inode and compares CoW block counts against rtrmapbt CoW ownership.

## Dependencies and Integration
Uses rtgroup cursors, rtrmapbt, rtbitmap used-space xref, metadata inode fork checks, and AG rmap cursor for metadata-inode block ownership.

## Risk and Edge Cases
- Requires both rtgroup rmap/refcount context and data-device rmap context for full xref.
- As in `refcount.c`, the mergeability helper appears to return false when the previous record has nonzero length, limiting intended detection.
- `xchk_xref_is_rt_cow_staging` sets corruption through `sc->sa.refc_cur` in one branch, while realtime checks otherwise use `sc->sr.refc_cur`.
