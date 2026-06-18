# sources/storage-engines/tikv/components/raftstore-v2/src/operation/ready/mod.rs

## Purpose
Drives raft ready processing for raftstore-v2. It batches raft side effects, sends asynchronous persistence tasks, applies committed entries, sends raft messages, manages snapshots, handles role changes, updates leases/read progress, reports durability/commit metrics, and finalizes peer destroy after persistence.

## Important APIs, Types, And Functions
Exports `ApplyTrace`, `DataTrace`, `StateStorage`, `AsyncWriter`, `GenSnapTask`, `SnapState`, and `write_initial_states`. `ReplayWatch` records startup replay pause statistics. Store APIs include `on_store_unreachable` and test-only `on_wait_flush`. Peer FSM tick APIs include `on_raft_tick` and `on_check_long_uncommitted`. Major peer methods include `maybe_pause_for_replay`, `tick`, `on_raft_message`, `on_raft_log_fetched`, `build_raft_message`, `send_raft_message`, `handle_raft_committed_entries`, `handle_raft_ready`, `on_persisted`, `on_role_changed`, `on_leader_commit_index_changed`, `check_long_uncommitted_proposals`, and `handle_reported_disk_usage`. `Storage::handle_raft_ready` folds ready state into write tasks.

## Control Flow
Ticks retry pending reads, check force leader state, and tick raft unless the peer is snapshot-handling or not serving. Incoming raft messages pass replay pause, tombstone, extra-message, epoch, peer-id, split-initialization, read-index fast path, and raft `step` handling before marking ready. `handle_raft_ready` resets ready flags, takes raft ready, handles role changes, sends volatile leader messages, applies read states, schedules committed entries to apply, builds a `WriteTask`, merges storage state changes and apply-trace writes, attaches persisted messages, starts destroy if the peer stopped serving, and either advances immediately for empty writes or advances asynchronously through `AsyncWriter`.

## State And Persistence Behavior
Ready persistence includes raft entries, hard state, raft state, apply trace records, snapshot application metadata, flushed epoch, and destroy tombstone writes. `AsyncWriter` delays `advance_append` completion until persistence returns. `on_persisted` sends deferred persisted messages, calls raft `on_persist_ready`, reports persisted/commit metrics, finalizes applied snapshot state, updates flushed epoch and entry cache persistence, cleans stale SSTs after persisted flushed-index records, optionally forwards force-leader commit index, and finishes destroy when all ready work is persisted.

## Dependencies And Integration Points
Depends on raft-rs `Ready`, raftstore transport, apply scheduling, snapshot module, async writer, apply trace, lifecycle destroy methods, query pending-read handling, PD heartbeat on role changes, coprocessor role/region-change notifications, tablet worker trim/flush tasks, disk usage tracking, transaction context, transfer-leader cache warmup, and raftstore metrics.

## Risks And Edge Cases
The file is concurrency-sensitive because ready handling and write completion can overlap. Persisted messages must wait for durable state, destroy must be the final ready, and snapshots must update apply state only after async loading completes. Read safety requires role-change cleanup, lease renewal/expiration, split and merge gating, and prepare-merge lease suspicion. Replay pause prevents startup from spending too long reading missing logs but must still schedule apply. Disk usage messages can change inflight limits and proposal availability. Failpoints cover snapshot-ready and long-uncommitted paths.

## Test Signals
No local test module appears here, but many integration tests exercise this path. Signals include ready metrics, persisted/commit waterfall metrics, snapshot counters, role-change coprocessor callbacks, long-uncommitted warnings, failpoints `before_handle_snapshot_ready_3` and `on_check_long_uncommitted_proposals_1`, test-export flush waits, and lifecycle tests that verify destroy completion after async persistence.
