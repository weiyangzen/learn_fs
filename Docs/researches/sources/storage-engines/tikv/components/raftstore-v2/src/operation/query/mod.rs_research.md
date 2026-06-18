# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/mod.rs

## Purpose
Coordinates all raftstore-v2 query handling. It separates KV reads from status queries, chooses local read versus read-index policy, validates query requests, applies read states from raft ready, and updates read progress after apply.

## Important APIs, Types, And Functions
`PeerFsmDelegate::on_query` is the main peer-FSM entry point. `inspect_read` chooses `ReadLocal` or `ReadIndex`. `Peer::validate_query_msg`, `read_index`, `apply_reads`, `post_pending_read_index_on_replica`, `ready_to_handle_unsafe_replica_read`, `ready_to_handle_read`, `send_read_command`, `on_query_status`, `query_status`, `on_query_debug_info`, and `handle_read_on_apply` implement query behavior. The module also declares `capture`, `lease`, `local`, and `replica` submodules.

## Control Flow
Non-status queries are validated for allowed command types, store id, stale-read exclusion, leadership or replica-read permission, peer id, force-leader state, initialization, term, and region epoch. Leaders can answer locally if applied to current term and lease is valid; otherwise they use read-index. Followers use read-index for explicit read-index or replica reads. `apply_reads` consumes raft ready read states, advances leader or replica pending-read queues, renews leader lease after successful read state, and clears stale reads after role changes. After apply, leaders or followers reattempt pending reads that were blocked by apply progress.

## State And Persistence Behavior
Query state is in-memory: pending reads, read progress, leader lease, role state, and debug metadata. No query path writes durable state directly, but read-index and no-op lease renewal interact with raft ready and may produce persisted raft entries. `on_query_debug_info` synthesizes v2 commit index and term from in-memory/persisted raft log state because v2 does not persist them in the same shape as v1.

## Dependencies And Integration Points
Depends on raft ready read states, `ReadIndexContext`, `ReadProgress`, `RequestPolicy`, proposal control, raft metrics, local reader delegates, lease and replica modules, coprocessor host notifications, `RegionMeta`, and query/debug channels.

## Risks And Edge Cases
Read safety is guarded by multiple conditions: applied term must match current term, split and merge states suppress unsafe reads, prepare-merge prevents replica read, and follower replica reads must wait until applied index reaches read index. Read-index responses can be lost on followers, so addition requests are re-proposed. Region epoch is checked before serving read-index responses. Role changes silently drop uncommitted reads and update read progress.

## Test Signals
Direct tests are in submodules, especially `query/local.rs`. Additional signals include failpoint `on_applied_current_term`, read-index pending counts, invalid proposal metrics, status query responses, debug info contents, and integration tests for leader transfer, follower reads, split/merge, and region epoch validation.
