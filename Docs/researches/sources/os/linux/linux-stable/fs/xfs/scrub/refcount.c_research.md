# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/refcount.c

## Purpose
Scrubs per-AG XFS refcount btrees. It verifies refcount records structurally, cross-checks them against allocation, inode, and rmap metadata, validates shared-vs-CoW ordering, and exposes helper xref checks for other scrubbers.

## Major Components
- `xchk_setup_ag_refcountbt`: enables intent draining when needed, runs repair setup if repair is possible, then initializes AG btree scrub context.
- Fragment-based rmap verification:
  - `xchk_refcountbt_rmap_check`
  - `xchk_refcountbt_process_rmap_fragments`
  - `xchk_refcountbt_xref_rmap`
- Record validation:
  - `xchk_refcountbt_rec`
  - `xchk_refcountbt_check_mergeable`
  - `xchk_refcountbt_xref_gaps`
- Whole-tree scrub:
  - `xchk_refcountbt`
- Public xref helpers:
  - `xchk_xref_is_cow_staging`
  - `xchk_xref_is_not_shared`
  - `xchk_xref_is_not_cow_staging`

## Control Flow and Invariants
The scrubber walks each refcountbt record with `xchk_btree`. For each record it:
- Converts the ondisk record to `xfs_refcount_irec`.
- Calls `xfs_refcount_check_irec`.
- Tracks CoW block count.
- Verifies shared records precede CoW records.
- Checks whether adjacent records should have been merged.
- Cross-references with used-space and inode-allocation metadata.
- Verifies refcount values by counting overlapping rmap records.

The rmap cross-check handles full-covering rmap records immediately and stores partial overlaps as ordered fragments. It then ensures the fragment working set maintains exactly the missing reference count over the whole refcount extent.

Gaps between shared refcount records are checked against rmap records to ensure no unrecorded shared extents exist.

## Dependencies and Integration
Depends on:
- `xfs_refcount_*` for refcountbt record conversion, lookup, and range queries.
- `xfs_rmap_query_range` and rmap cursors for ownership validation.
- `xchk_btree` framework for btree walking.
- `repair.h` setup hooks for optional online repair preparation.

Other scrubbers call the xref helpers to assert that blocks are not shared, not CoW staging, or are known CoW staging extents.

## Risk and Edge Cases
- Fragment verification assumes rmap records arrive in increasing block order; disorder is treated as corruption.
- Single-reference refcount records must represent CoW staging and are corrupt if owned by anything else.
- Gap checking short-circuits if rmap xref is unavailable or skipped.
- The mergeability helper as written returns false when the previous record has nonzero length, which means mergeability detection is effectively disabled after initialization; this is notable because the comment says the opposite.
