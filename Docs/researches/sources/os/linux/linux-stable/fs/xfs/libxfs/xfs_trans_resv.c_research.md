# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_trans_resv.c

## Purpose

Computes transaction log reservations for XFS metadata operations. It sizes log reservations for writes, truncates, namespace operations, inode allocation/freeing, realtime growth, refcount/rmap deferred operations, attributes, quotas, superblock syncs, and atomic write completion.

## Main Responsibilities

- Provides low-level reservation helpers:
  - buffer logging overhead
  - buffer reservation sizing
  - inode logging reservation sizing
  - allocation/free btree block counts
  - refcount and realtime refcount btree block counts
  - realtime allocation block counts
- Computes reservations for:
  - data writes
  - truncates
  - creates, links, removals, renames, mkdir, symlink
  - inode create/free/change
  - attribute set/remove/invalidate
  - growfs data and realtime phases
  - quota updates and quota block allocation
  - superblock sync
  - deferred EFI/RUI/CUI/BUI completion
  - realtime EFI/RUI/CUI completion
  - atomic write ioend completion
- Initializes `struct xfs_trans_resv` in `xfs_trans_resv_calc`.

## Realtime-Specific Behavior

Realtime support appears in several paths:
- `xfs_rtalloc_block_count` accounts for bitmap/summary updates and rtrmapbt splits.
- `xfs_calc_finish_rt_efi_reservation` handles realtime extent freeing.
- `xfs_calc_finish_rt_rui_reservation` handles realtime reverse mapping updates.
- `xfs_calc_finish_rt_cui_reservation` handles realtime refcount updates.
- Write/truncate reservations take the maximum of data, realtime, deferred free, and refcount update transactions.

## Parent Pointer Behavior

Namespace reservations grow when parent pointers are enabled:
- create/link/symlink/mkdir add parent pointer set overhead
- remove adds parent pointer remove overhead
- rename accounts for replace/unlink/link or exchange cases
- log counts increase to allow attribute transaction rolls

## Atomic Write Behavior

The atomic write helpers compute:
- per-intent log overhead for BUI/CUI/RUI/EFI chains
- per-step completion reservation
- maximum atomic write size supported by current reservation
- required log geometry for a requested atomic write size
- updated `tr_atomic_ioend` reservation

## Important Invariants

- Reservation formulas often take the maximum of possible transaction chains, not their sum.
- Runtime reflink reservations now handle refcount updates separately; older inflated counts are retained for minimum log-size compatibility.
- Permanent log reservations are assigned to transactions that may roll.
- BUI/RUI/CUI intent log counts are added when reflink or rmap features are active.
- Many formulas intentionally preserve historical reservation behavior to avoid changing minimum log-size requirements unexpectedly.

## Dependencies

- Uses mount-derived maxlevels for alloc, rmap, refcount, rtrmap, and rtrefcount btrees.
- Depends on transaction space macros from `xfs_trans_space.h`.
- Uses log item space helpers for intent/done items.

## Research Notes

This file is one of the core safety margins for XFS metadata updates. Realtime rmap/refcount integration is present but deliberately separated into deferred-operation reservations, matching current transaction chaining behavior.
