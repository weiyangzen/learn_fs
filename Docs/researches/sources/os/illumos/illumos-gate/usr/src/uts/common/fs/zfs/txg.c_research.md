# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/txg.c

Implements ZFS transaction group lifecycle management: initialization, sync/quiesce thread control, open/quiesce/sync transitions, commit callback dispatch, wait/kick/delay helpers, active-txg verification, and per-txg intrusive lists.

Key elements:
- Top comment explains the txg state machine: open accepts mutations, quiescing waits for in-flight transactions, syncing writes stable state and executes synctasks.
- `txg_init()` allocates per-CPU txg state, initializes locks, condition variables, callback lists, and starting open txg.
- `txg_fini()` tears down locks/CVs/taskq/per-CPU storage after threads are stopped.
- `txg_sync_start()` starts quiesce and sync kernel threads.
- `txg_sync_stop()` waits through deferred txgs, signals exit, and waits for both threads.
- `txg_hold_open()`, `txg_rele_to_quiesce()`, `txg_register_callbacks()`, and `txg_rele_to_sync()` manage transaction holds and per-txg callback lists.
- `txg_quiesce()` advances the open txg and waits for all per-CPU hold counts to drain.
- `txg_sync_thread()` waits for timeout, scan activity, waiters, dirty threshold, or quiesced txg; then calls `spa_sync()` and dispatches callbacks.
- `txg_quiesce_thread()` waits for a requested future txg, quiesces the current open txg, and hands it to sync.
- `txg_delay()` rate-limits open txg writers when syncing/quiescing backlog exists.
- `txg_wait_synced()`, `txg_wait_synced_sig()`, `txg_wait_open()`, and `txg_kick()` provide external coordination.
- `txg_list_*()` implements per-txg intrusive linked lists over objects embedding `txg_node_t`.

Main dependencies and interactions:
- Depends on txg internals, DMU transaction internals, DSL pool/scan, ZIL, and CPR callbacks.
- Calls `spa_sync()` for actual pool sync.
- Uses `dsl_scan_active()`, dirty-data thresholds, `dmu_tx_do_callbacks()`, taskqs, DTrace probes, and condition variables.

Implementation notes:
- Per-CPU `tc_open_lock` lets most transactions enter the open txg with low contention; quiesce temporarily grabs all such locks to advance the open txg.
- Commit callbacks are moved out of per-CPU lists after sync and dispatched asynchronously on a lazily created taskq.
- `txg_verify()` asserts non-initial txgs are within the active window unless using `ZILTEST_TXG`.
- `txg_all_lists_empty()` is intentionally racy and documented as such.
