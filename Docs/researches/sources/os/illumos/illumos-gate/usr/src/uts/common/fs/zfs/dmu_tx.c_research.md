# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_tx.c

## Purpose

Implements DMU transaction construction, hold declaration, write/free/ZAP/bonus/spill/SA space accounting, pre-assignment I/O error probing, transaction-group assignment, dirty-data throttling waits, temporary quota/reservation enforcement, commit/abort callback handling, and debug validation that dirty buffers were covered by a declared hold.

## Main Entry Points

- `dmu_tx_create_dd()`, `dmu_tx_create()`, `dmu_tx_create_assigned()`: allocate normal or already-assigned transactions.
- `dmu_tx_hold_write()`, `dmu_tx_hold_write_by_dnode()`, `dmu_tx_hold_remap_l1indirect()`: declare write-side modifications and estimate space.
- `dmu_tx_hold_free()`, `dmu_tx_hold_free_by_dnode()`: declare range frees and preload indirect metadata needed by syncing.
- `dmu_tx_hold_zap()`, `dmu_tx_hold_zap_by_dnode()`, `dmu_tx_hold_bonus()`, `dmu_tx_hold_spill()`, `dmu_tx_hold_space()`: declare metadata, ZAP, bonus, spill, and raw space needs.
- `dmu_tx_hold_sa_create()`, `dmu_tx_hold_sa()`: declare System Attribute object, registry, layout, bonus, and spill effects.
- `dmu_tx_assign()`, `dmu_tx_wait()`: assign to an open txg or wait/retry when blocked by dirty data, suspended pool state, dnode txg ownership, quota, or ENOSPC pressure.
- `dmu_tx_commit()`, `dmu_tx_abort()`, `dmu_tx_callback_register()`, `dmu_tx_do_callbacks()`: finish transactions and invoke callbacks.

## Control Flow And State

Each hold is represented by `dmu_tx_hold_t` on `tx_holds`, optionally referencing a held `dnode_t` and carrying two refcount-style estimates: `txh_space_towrite` and `txh_memory_tohold`. Hold setup increments `dn_holds`; once a tx is assigned, dnodes also track `dn_assigned_txg` and `dn_tx_holds` so open-context mutations do not collide with the previous quiescing txg.

Write and free holds do more than account bytes. `dmu_tx_count_write()` and `dmu_tx_hold_free_impl()` deliberately read partial data blocks and relevant level-1 indirect blocks before assignment so I/O errors are discovered before callers modify DMU state. ZAP holds account worst-case microzap/fatzap mutation costs and may perform a lookup to force target leaf reads.

`dmu_tx_try_assign()` opens a txg, attaches all dnode holds, totals write and memory estimates, converts the write estimate through `spa_get_worst_case_asize()`, and asks the owning `dsl_dir` for a temporary reservation. It returns `ERESTART` for cases the caller can wait through: dirty-data throttle, suspended pool, or a dnode still assigned to the previous txg. `dmu_tx_unassign()` unwinds partially assigned dnodes and txg holds.

Dirty-data throttling uses `dmu_tx_delay()`, a tunable curve based on `zfs_dirty_data_max`, `zfs_delay_min_dirty_percent`, `zfs_delay_scale`, and `zfs_delay_max_ns`. `dmu_tx_wait()` chooses between dirty-space CV waits plus delay, txg sync waits, pool resume waits, and dnode `dn_notxholds` waits.

## Dependencies

Depends on dnode/dbuf locking and reference accounting, ZIO reads, txg hold/release APIs, DSL pool and directory reservation logic, ZAP lookup behavior, SA layout/registry objects, SPA failmode and dirty-data throttle state, and zfs_refcount debugging machinery.

## Risks

This file sits on a core correctness boundary: callers must declare enough holds before mutation, and assignment/unassignment must not leak dnode tx holds or txg holds. The pre-assignment reads are performance-sensitive but also fault-tolerance-sensitive. Dirty-data delay math assumes `dirty < zfs_dirty_data_max`. Debug hold validation in `dmu_tx_dirty_buf()` encodes subtle allowances for bonus/spill blocks, block-size changes, and new indirect levels.
