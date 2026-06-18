# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/txg_impl.h

This private header defines the implementation state for transaction group progression.

Core definitions:
- `tx_cpu` is per-CPU state with `tc_open_lock`, `tc_lock`, per-TXG CVs, per-TXG hold counts, per-TXG callback lists, and padding.
- `tx_state_t` stores the per-pool TXG state machine: per-CPU array, sync lock, open/quiescing/quiesced/syncing/synced txg IDs, open timestamp, waiting txg values, CVs, exit flags, sync/quiesce threads, and commit-callback taskq.

Important concurrency model:
- Frequent hold-count updates are fanned out by CPU to avoid a single hot lock.
- `tx_open_txg` is protected by every CPU's `tc_open_lock`, not by `tx_sync_lock`.
- Quiescing must acquire all `tc_open_lock`s before moving the open txg forward.

Risk-sensitive invariants:
- `tc_count[txg]` must reach zero on all CPUs before a txg is quiesced.
- Sync/quiesce CVs and waiting fields drive user waits and sync-thread progress.
- Commit callbacks are stored per TXG and dispatched after the corresponding sync boundary.
