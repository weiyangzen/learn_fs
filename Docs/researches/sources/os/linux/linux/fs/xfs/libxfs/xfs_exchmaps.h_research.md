# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_exchmaps.h

## Purpose

Declares the public libxfs interface and data structures for XFS exchange-mapping operations, including in-core deferred intent state, caller request/estimation state, flag masks, fork selection helpers, cache lifecycle, estimation, inode preparation, deferred finishing, validation, and scheduling.

## Main Interfaces

- Deferred state: `struct xfs_exchmaps_intent`.
- Request and estimate state: `struct xfs_exchmaps_req`.
- Flag masks: internal `__XFS_EXCHMAPS_INO2_SHORTFORM`, `XFS_EXCHMAPS_INTERNAL_FLAGS`, and caller-visible `XFS_EXCHMAPS_PARAMS`.
- Fork helpers: `xfs_exchmaps_whichfork()` and `xfs_exchmaps_reqfork()`.
- API declarations: `xfs_exchmaps_estimate_overhead()`, `xfs_exchmaps_estimate()`, intent cache init/destroy, `xfs_exchmaps_init_intent()`, `xfs_exchmaps_ensure_reflink()`, `xfs_exchmaps_upgrade_extent_counts()`, `xfs_exchmaps_finish_one()`, `xfs_exchmaps_check_forks()`, `xfs_exchange_mappings()`.

## Control Flow And Behavior

Callers populate `xfs_exchmaps_req` with two inodes, source offsets, block count, and operation flags, then zero the estimate-output fields before calling the estimator. The estimator fills block movement counts, reservation blocks, and exchange count. Scheduling converts a request into an `xfs_exchmaps_intent`, which deferred operations repeatedly feed to `xfs_exchmaps_finish_one()` until all mapping and post-operation cleanup work completes.

Fork helper functions derive data versus attr fork selection from `XFS_EXCHMAPS_ATTR_FORK` in either intent or request flags.

## State And Data Structures

`xfs_exchmaps_intent` stores mutable progress: list linkage, two inodes, current offsets, remaining blockcount, optional final sizes, and flags. `xfs_exchmaps_req` stores immutable caller parameters plus estimator outputs for data-device blocks, realtime blocks, transaction reservation blocks, and number of exchange steps.

## Dependencies

Requires XFS inode, transaction, fork, and exchange-range flag definitions from surrounding XFS headers. The implementation uses the declared global `xfs_exchmaps_intent_cache` for intent allocation.

## Risks And Invariants

- Callers must not pass internal flags through the public request path.
- Estimate-output fields must be initialized by the caller before estimation because the estimator adds to them.
- `XFS_EXCHMAPS_SET_SIZES` is data-fork-only in the implementation.
- Intent state is mutable across deferred transaction relogs and must be treated as owned by deferred exchange machinery once scheduled.
