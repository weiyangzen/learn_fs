# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_trans_resv.c

## Purpose

`xfs_trans_resv.c` calculates XFS transaction log reservations. It estimates worst-case log space and log operation counts for data writes, truncates, deferred operations, namespace changes, inode allocation/free, attributes, quotas, growfs, superblock updates, and atomic write completion.

## Main Content

- Defines buffer log overhead and generic buffer reservation calculations.
- Computes allocation/free btree block counts for allocbt/cntbt and optional rmapbt.
- Computes refcount and realtime refcount btree update reservation sizes.
- Computes inode logging reservation, accounting for in-memory btree root overhead that can exceed on-disk fork size.
- Computes inobt/finobt and inode chunk allocation/free reservations.
- Computes realtime allocation metadata reservation, including bitmap/summary and optional realtime rmap btree work.
- Calculates deferred intent completion reservations:
  - Data and realtime extent free.
  - Data and realtime rmap updates.
  - Data and realtime refcount updates.
  - Bmap updates.
- Calculates write and truncate reservations, including separate refcount update transactions and historical minimum-log-size behavior.
- Computes parent pointer xattr intent overhead for namespace transactions.
- Calculates rename, link, remove, create, tmpfile, mkdir, symlink, inode free, inode change, growdata, growrt, synchronous write, writeid, addafork, attribute invalidation/set/remove, quota, and superblock reservations.
- Computes namespace transaction log counts adjusted for parent pointer transaction rolls.
- Fills `struct xfs_trans_resv` in `xfs_trans_resv_calc`.
- Adjusts write/truncate/quota log counts for deferred BUI, CUI, and RUI intent items on reflink/rmap filesystems.
- Calculates default and custom atomic write ioend reservations:
  - Per-intent overhead.
  - Per-step completion reservation.
  - Maximum supported atomic write size for current reservation.
  - Minimum log blocks and new reservation for a requested size.

## Key Interfaces and Invariants

- Reservations intentionally overestimate many worst cases to avoid transaction overruns.
- Runtime reflink refcount updates run in separate transactions; minimum log size calculations preserve older behavior by folding refcount splits into write/truncate reservations.
- Realtime rmap and realtime refcount deferred updates are included in separate completion paths.
- Namespace reservations must be calculated after static attribute reservations because parent pointers depend on attr set/remove reservation sizes.
- Parent pointer support increases both reservation size and permanent log count for namespace operations.
- Atomic write sizing temporarily overrides `tr_atomic_ioend.tr_logres` to compute minimum log size, then restores the old value.
- A requested atomic write reservation fails if required minimum log blocks exceed the mounted log size.

## Dependencies

Depends on mount geometry, btree max levels, realtime bitmap helpers, quota formats, log intent item sizing, transaction space macros, parent pointer formats, and log minimum-size calculation.
