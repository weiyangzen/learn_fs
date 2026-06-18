# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.c

## Purpose

This is the core XFS allocation group free-space allocator. It manages free-space btrees, AGFL blocks, AGF verification, extent allocation/freeing, deferred extent frees, per-AG allocator preparation, and public allocation APIs.

## Main Responsibilities

- Compute static AG metadata and reservation space.
- Search and update BNOBT and CNTBT free-space btrees.
- Allocate extents by exact block, near block, current AG, or AG scan.
- Free extents and coalesce with neighboring free-space records.
- Maintain AGF free block, longest extent, AGFL, and btree block counters.
- Refill or shrink AGFL safely.
- Verify AGF and AGFL metadata.
- Integrate rmap updates, busy extent tracking, per-AG reservations, and transaction accounting.
- Provide deferred extent free and autoreap mechanisms.

## Major Functional Areas

### Geometry and Reservation Sizing

- `xfs_agfl_size` computes usable AGFL slots, accounting for v5 CRC header space.
- `xfs_refc_block` and `xfs_prealloc_blocks` compute static AG metadata layout based on reflink, rmapbt, and finobt.
- `xfs_alloc_set_aside` withholds filesystem-wide blocks to prevent AGFL and bmap btree split deadlocks.
- `xfs_alloc_ag_max_usable` subtracts permanent AG metadata and reserve blocks from total AG size.

### Btree Record Operations

- Lookup helpers wrap `xfs_btree_lookup` for equal, greater/equal, and less/equal searches and mark cursors active.
- `xfs_alloc_update` rewrites free-space records.
- `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, and `xfs_alloc_get_rec` convert and validate records.
- Corrupt records mark the relevant btree sick and return `-EFSCORRUPTED`.

### Allocation Candidate Selection

- `xfs_alloc_compute_aligned`
  - Trims busy extents, applies min/max AG block limits, and aligns candidate start blocks.
- `xfs_alloc_compute_diff`
  - Scores locality for near allocations.
- `xfs_alloc_fix_len`
  - Adjusts allocation length to satisfy `k * prod + mod`.
- `xfs_alloc_cur_*` helpers maintain multi-cursor search state across CNTBT and BNOBT.
- `xfs_alloc_ag_vextent_exact`
  - Allocates only if the requested block lies in a valid free extent and is not blocked by busy extents.
- `xfs_alloc_ag_vextent_near`
  - Uses parallel BNOBT and CNTBT searching for locality-sensitive allocations.
  - Flushes busy extents and retries, with try-flush first to avoid blocking deadlocks.
- `xfs_alloc_ag_vextent_size`
  - Best-fit allocation anywhere in an AG, primarily by CNTBT size ordering.
- `xfs_alloc_ag_vextent_small`
  - Handles small/extreme cases, including pulling one block from the AGFL if normal btrees are empty and constraints allow.

### Dual Btree Updates

`xfs_alloc_fixup_trees` is the central routine for removing allocated space from the free-space btrees:

- Deletes the original CNTBT record.
- Inserts zero, one, or two replacement CNTBT records.
- Deletes or updates the BNOBT record.
- Inserts a second BNOBT record when allocation splits a free extent.
- Detects when the largest CNTBT leaf might have changed and updates `agf_longest`.

Freeing uses `xfs_free_ag_extent`:

- Updates rmap unless caller asks to skip owner updates.
- Finds left and right BNOBT neighbors.
- Rejects overlapping frees as corruption.
- Coalesces left, right, both, or neither.
- Updates CNTBT and BNOBT consistently.
- Updates AGF counters and per-AG reservation accounting.
- Records stats and tracepoints.

### AGFL Management

- `xfs_alloc_min_freelist` calculates worst-case AGFL block needs for bno, cnt, and rmap btree splits.
- `xfs_alloc_space_available` decides whether allocation can proceed while preserving AGFL minimum, per-AG reservations, minleft, total transaction needs, and contiguous extent size.
- `xfs_agfl_needs_reset` detects AGFL index/count inconsistencies.
- `xfs_agfl_reset` empties corrupted AGFL state, warns about leaked blocks, and clears the reset flag.
- `xfs_alloc_fix_freelist`
  - Reads/initializes AGF as needed.
  - Rejects metadata-preferred AGs for user data during trylock scans.
  - Runs space-availability checks before and after AGF lock.
  - Shrinks overfull AGFL by deferring frees.
  - Refills short AGFL by allocating blocks and placing them onto the freelist.
  - Supports repair-only flags such as `NORMAP` and `NOSHRINK`.

### AGF and AGFL IO/Verification

- `xfs_agfl_verify`, read/write verifiers, and `xfs_agfl_buf_ops` validate CRC-format AGFLs.
- Non-CRC AGFL contents cannot be fully verified because old mkfs versions did not initialize all slots.
- `xfs_validate_ag_length` checks sequence and length against AG geometry.
- `xfs_agf_verify`, read/write verifiers, and `xfs_agf_buf_ops` validate magic, version, length, counters, btree levels, rmap/refcount fields, UUID, and LSN.
- `xfs_alloc_read_agf` initializes cached `pagf_*` fields and updates global allocbt block count, with DEBUG checks to detect stale AGF rereads.

### Public Allocation APIs

- `xfs_alloc_vextent_this_ag`
  - Best-fit allocation within a caller-held per-AG reference.
- `xfs_alloc_vextent_start_ag`
  - Locality-aware full-filesystem scan with nonblocking then blocking behavior.
  - Handles inode32 rotor behavior for initial user data.
- `xfs_alloc_vextent_first_ag`
  - Blocking scan from target AG to the end without wrapping below target.
- `xfs_alloc_vextent_exact_bno`
  - Exact block allocation within caller-held per-AG reference.
- `xfs_alloc_vextent_near_bno`
  - Near-target allocation in one AG, grabbing per-AG reference if needed.
- `__xfs_free_extent`
  - Fixes freelist, validates extent against locked AGF, frees into AG btrees, and inserts a busy extent.

### Deferred Free and Autoreap

- `xfs_defer_extent_free` creates sorted deferred free intent items.
- `xfs_free_extent_later` exposes deferred freeing.
- `xfs_alloc_schedule_autoreap`
  - Creates a paused deferred free item so log recovery can reclaim allocated-but-uncommitted space.
- `xfs_alloc_cancel_autoreap`
  - Marks pending free items canceled and unpauses them to log EFD without freeing.
- `xfs_alloc_commit_autoreap`
  - Unpauses deferred free so the allocated space will be freed.

### Query Helpers

- `xfs_alloc_query_range`
- `xfs_alloc_query_all`
- `xfs_alloc_has_records`
- `xfs_agfl_walk`

These support scrub/repair and other metadata scanners by validating free-space records before callback use.

## Important Invariants and Edge Cases

- AGF lock ordering is tracked with `tp->t_highest_agno`; later allocation attempts avoid lower AGs that could deadlock.
- Public allocation finish converts `NULLAGBLOCK` to `NULLFSBLOCK`, even if the lower-level path returned success.
- Allocation success updates rmap first, then AG free counters unless allocation came from AGFL.
- Busy extents are trimmed from candidates; allocation retries may flush busy extents.
- Freeing overlapping already-free space is corruption.
- AGFL blocks used for user data are invalidated in the transaction.
- AGFL reset intentionally leaks untrusted AGFL blocks to keep the filesystem online and asks the user to run repair.
- `XFS_ALLOC_FLAG_FREEING` allows freelist fixup even when normal allocation constraints would fail.
- `XFS_ALLOC_FLAG_TRYLOCK` failures are converted to skip-this-AG behavior.
- Debug-only `alloc_minlen_only` can require an exact minlen free extent.

## Dependencies

- BNOBT/CNTBT cursor ops from `xfs_alloc_btree.c`.
- Per-AG geometry/state from `xfs_ag.h`.
- Per-AG reservations from `xfs_ag_resv.c`.
- Rmap updates, busy extent tracking, transactions, deferred ops, health marking, tracing, and buffer verifiers.

## Research Notes

This is one of the highest-complexity files in the group. Its core correctness depends on keeping three views synchronized: on-disk AGF/AGFL, in-core `pagf_*` caches, and free-space btree records. The allocation paths are deliberately conservative around AGFL minima, per-AG reservations, busy extents, and transaction AG lock ordering.
