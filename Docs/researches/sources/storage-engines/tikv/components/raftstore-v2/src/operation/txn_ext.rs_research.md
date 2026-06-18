# sources/storage-engines/tikv/components/raftstore-v2/src/operation/txn_ext.rs

Purpose: this file manages transaction-side extensions tied to raftstore-v2 peer leadership: max timestamp synchronization, in-memory pessimistic lock lifecycle, lock movement during split, and lock persistence before leader transfer.

Important APIs/types/functions: `TxnContext` wraps `Arc<TxnExt>`, an atomic `ExtraOp`, and a tick counter for memory-lock reactivation. Key methods are `on_region_changed`, `on_became_leader`, `after_commit_merge`, `on_became_follower`, `split`, `init_with_lock`, and private `require_updating_max_ts`. Peer methods are `on_reactivate_memory_lock_tick` and `propose_locks_before_transfer_leader`.

Control flow: when a peer becomes leader or after merge, `require_updating_max_ts` encodes term and region version into `max_ts_sync_status`, then schedules `pd::Task::UpdateMaxTimestamp`; PD worker later advances the concurrency manager. Leadership changes update `PeerPessimisticLocks` status, term, and version. Before transfer-leader, the peer decodes `TransferLeaderContext`, disables in-memory locks by moving status to `TransferringLeader`, schedules a reactivation tick, encodes all non-deleted lock CF entries into a simple write, and proposes them before actual transfer if needed.

State and persistence: the in-memory pessimistic-lock map is guarded by `RwLock`; lock table version is deliberately advanced on split so concurrent readers fail with epoch mismatch instead of lock-not-found. Persistent lock materialization uses `SimpleWriteEncoder` against `CF_LOCK`, with `DiskFullOpt::AllowedOnAlmostFull` so transfer safety is not blocked by almost-full disk mode.

Dependencies/integration: depends on `raftstore::store::TxnExt`, `PeerPessimisticLocks`, transfer-leader context encoding, `SimpleWriteEncoder`, peer ticks, and PD worker timestamp update tasks. It ties into split admin handling through returned grouped locks.

Risks: the transfer path has a FIXME about raft command size limits when many locks are encoded. Status/tick ordering around `lead_transferee` is delicate; reactivation too early can reopen memory locks while transfer is still pending. Max-ts status uses packed low bits, so stale async PD responses are filtered only by exact atomic status.

Test signals: no direct unit tests in this file. Coverage is implied by leader transfer, pessimistic transaction, split, and merge integration tests elsewhere; failpoint `invalidate_locks_before_transfer_leader` targets the persistence window.
