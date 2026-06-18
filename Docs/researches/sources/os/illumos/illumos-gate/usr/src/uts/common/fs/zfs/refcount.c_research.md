# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/refcount.c

## Scope

This file implements ZFS debug refcount tracking under `ZFS_DEBUG`. In non-debug builds this file contributes no compiled implementation because the entire body is conditional. The file was read completely.

## APIs And Entry Points

- Global lifecycle: `zfs_refcount_init()`, `zfs_refcount_fini()`.
- Creation/destruction: `zfs_refcount_create()`, `zfs_refcount_create_tracked()`, `zfs_refcount_create_untracked()`, `zfs_refcount_destroy()`, `zfs_refcount_destroy_many()`.
- Counting: `zfs_refcount_count()`, `zfs_refcount_is_zero()`.
- Add/remove: `zfs_refcount_add_many()`, `zfs_refcount_add()`, `zfs_refcount_add_few()`, `zfs_refcount_remove_many()`, `zfs_refcount_remove()`, `zfs_refcount_remove_few()`.
- Ownership and inspection: `zfs_refcount_transfer()`, `zfs_refcount_transfer_ownership_many()`, `zfs_refcount_transfer_ownership()`, `zfs_refcount_held()`, `zfs_refcount_not_held()`.

## Control Flow

A refcount can be tracked or untracked. Untracked refcounts update `rc_count` atomically and do not remember individual holders. Tracked refcounts allocate `reference_t` records from a kmem cache and store them in an AVL tree keyed by holder pointer and reference number. This lets debug builds detect removing a hold that was never added and query whether a specific holder is present.

Removal in tracked mode finds the exact holder/count record, removes it from the AVL tree, decrements `rc_count`, and optionally keeps recently removed references in `rc_removed` for postmortem history. The history length is controlled by `reference_history`.

Transfer operations move all references from one refcount to another, including active tree entries and removed-history entries. Ownership-transfer operations retag an existing holder to a new holder without changing the count.

## State And Dependencies

Global state includes `reference_tracking_enable`, `reference_history`, and two kmem caches. Each `zfs_refcount_t` contains a mutex, AVL tree of live references, list of removed-history records, count fields, and a tracked flag.

In this group, `metaslab.c` uses tracked refcounts for allocation slots and metaslab group allocation queue depth, giving debug visibility into allocation throttle reservations.

## Risks And Invariants

- `zfs_refcount_destroy_many()` asserts the expected final count, so callers must drain holds or pass the expected residual count.
- Tracked removal panics if the holder/count pair does not exist, which is intentional debug enforcement.
- In untracked mode, holder-specific queries are conservative: “held” means count is nonzero, and “not held” always returns true because individual holders are unknown.
- `zfs_refcount_add_few()` and remove-few split into individual records in tracked mode so later per-holder removals can match one hold at a time.
- Transfer merges AVL entries into the destination and preserves removed-history lists; callers must avoid conflicting live holder/count identities.

## Summary

`refcount.c` is a debug-only accountability layer around reference counts. It lets ZFS use cheap atomic counts when tracking is disabled and detailed holder records when diagnosing leaks, double-removes, or allocation-throttle bookkeeping errors.
