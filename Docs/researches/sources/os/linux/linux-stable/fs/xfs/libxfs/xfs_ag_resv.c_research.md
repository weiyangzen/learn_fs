# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.c

## Purpose

This file implements per-allocation-group block reservations for XFS metadata structures that may need to grow even when an AG is nearly full, especially refcount and reverse mapping btrees.

## Main Responsibilities

- Track metadata and rmapbt reservation availability per AG.
- Hide reserved space from free block accounting.
- Initialize reservation sizes from refcountbt, finobt, and rmapbt reserve calculations.
- Charge allocations against reservation pools.
- Return freed blocks to reservation pools when appropriate.
- Detect critically low reservation state.

## Key Functions

- `xfs_ag_resv_critical`
  - Reports whether metadata or rmapbt reservation is critically low.
  - Threshold is less than 10 percent of asked reservation or less than maximum AG btree height.
  - Supports error-tag injection.
- `xfs_ag_resv_needed`
  - Returns reserved-but-unavailable blocks that allocator callers must preserve.
  - Excludes the reservation pool being used by the current allocation.
- `xfs_ag_resv_free`
  - Releases rmapbt and metadata reservations and restores fdblocks/accounting.
- `xfs_ag_resv_init`
  - Calculates and establishes metadata and rmapbt reservations.
  - Metadata reservation includes refcountbt and finobt needs.
  - If full metadata reservation fails, it falls back to refcountbt-only reservation and sets `m_finobt_nores`.
  - Initializes AGF state when any reservation exists so free-space counters are ready.
  - Returns `-ENOSPC` if requested reservations exceed available AG free/AGFL blocks.
- `xfs_ag_resv_alloc_extent`
  - Decrements reservation counters for allocations.
  - Updates transaction superblock counters differently for reserved versus non-reserved blocks and rmapbt.
- `xfs_ag_resv_free_extent`
  - Replenishes reservations on frees.
  - Updates reserved and normal fdblocks accounting based on how much fits back into the reservation.

## Reservation Model

- Reservations are virtual in-core accounting, not persistent allocations, avoiding crash cleanup.
- Metadata reservation hides only unused reserved metadata blocks because already-used metadata is on-disk allocated.
- RMAPBT reservation hides the entire ask because rmapbt blocks live in free-space/AGFL accounting.
- AG 0 adjusts filesystem-wide `m_ag_max_usable`, assuming it has the maximum per-AG reservation need.

## Important Invariants and Edge Cases

- `used > ask` is normalized by increasing `ask` to `used`.
- Unknown reservation types assert and fail or fall back as appropriate.
- AGFL and metafile reservation types do not consume normal per-AG reservation accounting in allocation/free hooks.
- RMAPBT reservation accounting avoids fdblocks updates during per-allocation charge/free because its blocks come from AGFL/free-space accounting.
- A reservation initialization failure warns that the filesystem may run out of space for metadata expansion.

## Dependencies

- Refcountbt, finobt, rmapbt reserve calculators.
- Free block counter helpers.
- AGF initialization through `xfs_alloc_read_agf`.
- Tracing and error-tag injection.

## Research Notes

This file is tightly coupled to allocator space-availability decisions. `xfs_alloc_space_available` and `xfs_alloc_longest_free_extent` use `xfs_ag_resv_needed` to keep virtual reservation promises while still allowing the reserving subsystem to consume its own pool.
