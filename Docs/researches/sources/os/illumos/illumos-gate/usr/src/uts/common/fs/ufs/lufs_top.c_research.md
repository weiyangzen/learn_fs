# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_top.c

## Purpose

`lufs_top.c` implements the transaction operation layer for UFS logging. It coordinates synchronous and asynchronous transaction entry/exit, reservation accounting, commit sequencing, forced empty sync transactions, delta declaration/cancellation, and movement of dirty metadata into the log.

## Main Interfaces

Key routines include `top_delta`, `top_cancel`, `top_iscancel`, `top_seterror`, `top_begin_sync`, `top_begin_async`, `top_end_sync`, `top_end_async`, `top_read_roll`, `top_log`, and `_init_top`.

## Transaction Flow

`top_begin_sync()` enters a synchronous transaction, waits if the current transaction is closed or over-reserved, handles fsync-specific fast failure for `T_DONTPEND` threads, and reserves log space. `top_begin_async()` enters async work unless the async side is closed or the transaction is over-reserved; when needed, it dispatches an empty sync operation on `system_taskq` to drain reservations.

`top_end_sync()` is the commit path. The last sync operation closes the current transaction to sync and async callers, waits for active async work, pushes remaining deltamap entries, writes a commit record, waits for log writes, frees canceled deltas only after commit durability, opens the next transaction, wakes waiters, and may force log rolling.

`top_end_async()` releases reservation slack, records the last async transaction id when deltas were generated, wakes sync commit waiters when it was the final async operation, and triggers sync/roll pressure handling when maps or log usage are high.

## Delta And Logging Operations

`top_delta()` records metadata ranges into the deltamap and marks the current thread transaction as having deltas. `top_cancel()` removes metadata deltas and adds logmap cancel records. `top_log()` removes deltas from the deltamap and adds them to the logmap, using cached roll buffers when possible.

`top_read_roll()` is called by the roll thread to gather logmap entries for a master block, choose cached-roll-buffer or read/overlay behavior, and initiate asynchronous master reads when required.

## Notable Invariants And Risks

- Thread-specific `threadtrans_t` state is stored under `topkey`.
- `un_resv`, `un_resv_wantin`, `mtm_active`, `mtm_activesync`, and `mtm_wantin` are the main reservation/concurrency counters.
- Commit ordering deliberately allows async operations before the commit write completes, but holds `un_log_mutex` so no new deltas are written before the commit record is durable.
- Audit hotspots are forced sync taskq counting, condition-variable sequencing, fsync `T_DONTPEND` behavior, commit/cancel durability ordering, and reservation arithmetic under error paths.
