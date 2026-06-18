# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc.c

## Purpose

`xfs_alloc.c` is the core allocation-group free-space manager for libxfs. It owns AGF/AGFL verification and update paths, allocation from the paired free-space btrees, free-space insertion/merge, per-AG freelist refill/shrink, top-level extent allocation wrappers, deferred extent-free item creation, and AGFL walking/query helpers.

The file is userspace-shared XFS logic: although it contains kernel-style cache/workqueue globals, it is written around libxfs transactions, buffers, btree cursors, per-AG state, reverse mapping updates, extent busy tracking, and AG reservations.

## Main Structures and State

- `xfs_extfree_item_cache`: slab cache for deferred extent-free intent items.
- `xfs_alloc_wq`: exported workqueue pointer for allocation work.
- `struct xfs_alloc_cur`: internal multi-cursor allocation search state. It holds a cntbt cursor, two bnobt cursors for left/right locality scanning, the current best free-space record, chosen allocation start/length, locality diff, busy-generation state, and whether busy extents were encountered.
- AGF state mirrors: functions update both on-disk AGF fields and in-core `xfs_perag` fields, especially `pagf_freeblks`, `pagf_flcount`, `pagf_longest`, btree levels, and btree block counters.
- Deferred free items: `xfs_defer_extent_free` populates `struct xfs_extent_free_item` with owner, flags, start block, block count, AG reservation type, group pointer, and realtime/skip-discard/attr-fork/bmbt flags.

## Allocation Geometry Helpers

- `xfs_agfl_size` computes usable AGFL entries, accounting for the v5 CRC AGFL header.
- `xfs_refc_block` and `xfs_prealloc_blocks` compute early metadata block reservations based on reflink, rmapbt, finobt, and inode btree features.
- `xfs_alloc_set_aside` computes global blocks withheld from fdblocks so nearly full AGs can refill AGFLs and split bmap btrees safely.
- `xfs_alloc_ag_max_usable` computes maximum allocatable AG payload after permanent metadata and AGFL reserve blocks.
- `xfs_alloc_compute_maxlevels`, `xfs_alloc_min_freelist`, and `xfs_alloc_longest_free_extent` derive btree height limits, minimum AGFL refill needs, and longest usable extent after AGFL and reservation pressure.

## Free-Space Btree Operations

The file maintains two free-space btrees:
- bnobt: keyed by start block.
- cntbt: keyed by length then start block.

Key helpers:
- `xfs_alloc_lookup`, `xfs_alloc_lookup_eq/ge/le` set `cur->bc_rec.a` and call generic btree lookup. They also toggle `XFS_BTREE_ALLOCBT_ACTIVE` to track cursor search liveness.
- `xfs_alloc_update` writes a new free-space record at the cursor.
- `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, `xfs_alloc_get_rec`, and `xfs_alloc_complain_bad_rec` convert and validate free-space records, marking btrees sick on corruption.
- `xfs_alloc_fixup_trees` removes an allocated subrange from a free-space record and updates both trees. It handles all split cases: consume whole record, consume left edge, consume right edge, or split into two free records.
- `xfs_alloc_cursor_at_lastrec`, `xfs_cntbt_longest`, and `xfs_alloc_fixup_longest` maintain `agf_longest` / `pagf_longest` when modifications touch the cntbt right edge.

## Allocation Algorithms

The file implements exact, near, and anywhere-in-AG allocation modes.

- `xfs_alloc_compute_aligned` trims busy extents out of a candidate, clamps to min AG block, and applies alignment.
- `xfs_alloc_compute_diff` chooses a start inside a free extent that is closest to the target while respecting alignment, requested length, and user-data contiguity heuristics.
- `xfs_alloc_fix_len` adjusts returned length to satisfy `prod/mod` constraints while staying within min/max.
- `xfs_alloc_ag_vextent_small` handles small fallback allocation from the last cntbt record or, for 1-block allocations, from AGFL if legal.
- `xfs_alloc_ag_vextent_exact` looks up the bnobt record containing the requested block, trims busy portions, computes allowable length, and fixes both btrees.
- `xfs_alloc_ag_vextent_near` combines cntbt and bnobt scans for locality. It has fast last-block scanning, parallel left/right bnobt walking, cntbt size-key iteration, busy-extent flush/retry, and final btree fixup.
- `xfs_alloc_ag_vextent_size` performs best-fit "anywhere in this AG" allocation using cntbt, with fallback to smaller extents and busy-extent retry.
- `xfs_alloc_cur_setup`, `xfs_alloc_cur_check`, `xfs_alloc_cntbt_iter`, `xfs_alloc_walk_iter`, and `xfs_alloc_cur_finish` implement the reusable cursor-based near-allocation engine.

Busy extents are handled conservatively: candidate extents are trimmed, busy generations are captured, and `xfs_extent_busy_flush` is used for retry. `XFS_ALLOC_FLAG_TRYFLUSH` enables a quick first retry before blocking behavior.

## Freeing Algorithm

`xfs_free_ag_extent` frees an AG-relative extent:

1. Optionally removes the reverse mapping unless owner updates are skipped.
2. Looks for left and right bnobt neighbors.
3. Detects overlap/corruption if the extent is already partially free.
4. Deletes old cntbt entries for neighbors.
5. Merges with left, right, both, or inserts a new free record.
6. Inserts the merged record into cntbt.
7. Fixes `agf_longest` if required.
8. Updates free block counters and AG reservation accounting.

`__xfs_free_extent` is the exported free wrapper. It fixes/refills the freelist first, validates the extent against AGF length, calls `xfs_free_ag_extent`, and inserts the freed range into the busy extent list, optionally skipping discard.

## AGFL and AGF Management

AGFL:
- `xfs_agfl_verify`, `xfs_agfl_read_verify`, `xfs_agfl_write_verify`, and `xfs_agfl_buf_ops` validate CRC-enabled AGFL headers, UUIDs, sequence numbers, LSNs, and entries.
- `xfs_alloc_read_agfl` reads and references the AGFL buffer.
- `xfs_alloc_get_freelist` pops from AGFL, updates `flfirst`, `flcount`, perag counters, and btree block counts.
- `xfs_alloc_put_freelist` pushes to AGFL, updates `fllast`, `flcount`, perag counters, and logs the written slot.
- `xfs_agfl_needs_reset` detects inconsistent AGFL ring fields, including old padding mismatch cases.
- `xfs_agfl_reset` empties a corrupted AGFL, logs the reset, clears perag reset state, and warns that repair is needed to recover leaked blocks.
- `xfs_agfl_walk` iterates active AGFL entries from first to last with wraparound.

AGF:
- `xfs_validate_ag_length` checks sequence number and AG length, with growfs exceptions.
- `xfs_agf_verify`, `xfs_agf_read_verify`, `xfs_agf_write_verify`, and `xfs_agf_buf_ops` validate AGF magic, version, UUID, LSN, freelist indexes, free/longest counters, btree levels, rmap/refcount counters, and checksums.
- `xfs_read_agf` reads the AGF buffer.
- `xfs_alloc_read_agf` initializes perag AGF mirrors on first read, detects AGFL reset needs, updates the global allocbt block count, and debug-checks stale AGF rereads.
- `xfs_alloc_log_agf` maps AGF field masks to byte ranges and logs the minimal buffer region.
- `xfs_alloc_update_counters` updates `agf_freeblks` and `pagf_freeblks`, detects impossible free count overflow, and logs AGF free blocks.

## Freelist Fixup and Top-Level Allocation

`xfs_alloc_fix_freelist` is the gatekeeper before allocating or freeing in an AG. It:
- Reads/initializes AGF.
- Skips metadata-preferred AGs for user data during trylock scans.
- Checks if the AG can satisfy allocation plus AGFL/reservation needs.
- Resets a bad AGFL before modifying it.
- Optionally enforces exact-minlen debug behavior.
- Shrinks AGFL by popping extra AGFL blocks and deferring frees.
- Refills AGFL by allocating free-space extents, adding rmaps, decrementing free counters, and pushing each block onto AGFL.

Top-level allocation wrappers:
- `xfs_alloc_vextent_this_ag`: allocate anywhere in a specified AG with caller-held perag.
- `xfs_alloc_vextent_exact_bno`: allocate exactly at a target fsblock within caller-held perag.
- `xfs_alloc_vextent_near_bno`: allocate near target in one AG, grabbing perag if needed.
- `xfs_alloc_vextent_start_ag`: best-effort whole-filesystem scan. It starts with locality in the target AG, then falls back to non-localized AG iteration. It does trylock then blocking behavior and handles inode32 rotor placement.
- `xfs_alloc_vextent_first_ag`: last-resort blocking scan from target AG to the end without wrapping below the target.

Shared wrappers:
- `xfs_alloc_vextent_check_args` normalizes arguments and enforces bounds.
- `xfs_alloc_vextent_prepare_ag` obtains perag if needed and fixes freelist.
- `xfs_alloc_vextent_finish` turns AG block results into fsblocks, updates transaction AG lock-order tracking, updates rmaps and counters, consumes AG reservations, records stats, and releases perag if requested.
- `xfs_alloc_vextent_iterate_ags` implements wrapped AG scanning while respecting transaction highest-AG locking constraints.

## Deferred Free and Autoreap

- `xfs_defer_extent_free` validates normal or realtime extents and queues an `xfs_extent_free_item` through the defer subsystem.
- `xfs_free_extent_later` is the public helper for deferred frees.
- `xfs_alloc_schedule_autoreap` creates a paused deferred free item so newly allocated unwritten space can be automatically reaped by log recovery if the system crashes before cancellation.
- `xfs_alloc_cancel_autoreap` marks paused free items cancelled and unpauses them, logging cancellation instead of freeing.
- `xfs_alloc_commit_autoreap` unpauses a scheduled autoreap so the deferred free proceeds.

## Query Helpers and Cache Lifecycle

- `xfs_alloc_query_range` and `xfs_alloc_query_all` wrap generic btree query APIs for bnobt records, validating each record before callback.
- `xfs_alloc_has_records` asks whether a block range has no, partial, or full free-space record coverage.
- `xfs_extfree_intent_init_cache` and `xfs_extfree_intent_destroy_cache` manage the deferred extent-free item cache.

## Invariants and Failure Handling

Important invariants:
- Every free-space modification must keep bnobt and cntbt equivalent.
- `agf_longest` must reflect the largest cntbt record.
- AGF free block counters cannot exceed AG length.
- AGFL ring fields must stay inside `xfs_agfl_size`.
- Allocation must not consume blocks required for AGFL refill, reservations, or caller `minleft`.
- Btree block allocation/free uses AGFL and keeps `m_allocbt_blks` and `agf_btreeblks` coherent.
- Reverse mapping updates are skipped only through explicit owner-info skip paths.

Failure behavior is defensive: corrupted records mark the relevant btree or AG sick and return `-EFSCORRUPTED`; metadata I/O sickness propagates AG health marks; trylock AGF read failures become AG skips; allocation misses generally return success with `NULLFSBLOCK`, preserving historical XFS allocation API behavior.

## Dependencies

This file depends on generic btree code, allocation btree cursor constructors, transaction/buffer logging, perag state, AG reservation accounting, rmap updates, busy extent tracking, bmap ownership flags, health marking, tracepoints, and deferred intent infrastructure.

## Risk Areas

- AGFL refill/shrink is transaction-sensitive and can create log reservation pressure, so frees are deferred.
- Lock ordering across AGFs is guarded through `t_highest_agno`; changing iteration behavior can reintroduce ABBA deadlocks.
- Busy extent trimming and retry directly affect allocator correctness under delayed free/discard pressure.
- `agf_longest`, perag counters, and AGF fields must be updated together; partial updates can cause ENOSPC errors or corruption reports.
- Repair-specific `NORMAP` and `NOSHRINK` flags are present in shared libxfs code and must remain compatible with xfs_repair behavior.
