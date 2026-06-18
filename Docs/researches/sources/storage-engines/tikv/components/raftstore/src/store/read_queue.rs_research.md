# sources/storage-engines/tikv/components/raftstore/src/store/read_queue.rs

## Purpose
`read_queue.rs` manages pending ReadIndex requests for region peers. It batches client callbacks behind raft read-index contexts, advances requests when raft returns read states, tracks readiness separately from queue position, and serializes/deserializes the opaque context bytes carried through raft. It supports both leader-local ordering and follower/replica out-of-order responses.

## Important APIs, Types, and Functions
`ReadIndexRequest<C>` stores one logical read-index context UUID, the pending raft commands and callbacks, the proposal timestamp, optional resolved read index, optional extra `ReadIndexRequest` protobuf for lock checking, optional `LockInfo`, and an `in_contexts` flag indicating whether the UUID is still tracked in the queue's context map. `push_command`, `with_command`, `cmds`, and `take_cmds` are the main request APIs. `Drop` records pending duration metrics.

`ReadIndexQueue<C>` stores a `VecDeque<ReadIndexRequest<C>>`, `ready_cnt`, `handled_cnt`, a `HashMap<Uuid, usize>` from UUID to absolute queue offset, retry countdown, and log tag. Its main APIs are `check_needs_retry`, `has_unresolved`, `clear_all`, `clear_uncommitted_on_role_change`, `push_back`, `advance_leader_reads`, `advance_replica_reads`, `pop_front`, `push_front`, and `gc`.

`ReadIndexContext` encodes the raft context payload. The first 16 bytes are always the UUID. Optional tagged fields carry a protobuf `raft_cmdpb::ReadIndexRequest`, protobuf `LockInfo`, and a `read_index_safe_ts` u64. `parse`, `to_bytes`, and `fields_to_bytes` provide backward-compatible serialization; a bare UUID remains valid old-format context.

## Control Flow
Requests enter via `ReadIndexRequest::with_command` and `ReadIndexQueue::push_back`. Leader requests are queued without UUID map entries because leader read states are expected to advance strictly in queue order. Follower/replica requests are inserted into `contexts` with an absolute offset equal to `handled_cnt + reads.len()` so later pops do not invalidate stored offsets.

Retry handling is tick-based. `check_needs_retry` returns false if all queued reads are already ready, uses `usize::MAX` as a just-pushed sentinel, decrements countdown while waiting, and returns true when unresolved requests should be retried through raft.

Leader advancement uses `advance_leader_reads`, comparing each returned UUID with `reads[ready_cnt]`. A mismatch logs surrounding expected/actual UUID context and panics, preserving the invariant that leader read states must arrive in request order. Replica advancement uses `advance_replica_reads`, removes UUIDs from `contexts`, converts absolute offsets back to current deque offsets by subtracting `handled_cnt`, records lock information, clears `addition_request` to signal lock checking completion, and updates `read_index` to the lowest observed index when multiple states touch the same request. It then marks all requests through the highest changed offset ready, allowing out-of-order replica responses to release a prefix.

Ready requests are consumed with `pop_front`, which decrements `ready_cnt`, increments `handled_cnt`, removes still-tracked contexts, and returns the request. `push_front` requeues a popped ready request when raft cannot yet process it, restoring `ready_cnt` and `handled_cnt`.

## State and Persistence Behavior
The queue is memory-only; persistence happens through raft's read-index mechanism rather than local storage. Metrics are stateful side effects: pending count increments when commands are added, decrements on queue clearing, and pending duration is observed on `ReadIndexRequest` drop. Memory accounting is implemented in the `memtrace` module through `HeapSize`, including command heap usage, optional extra request memory, deque capacity, and context-map estimates.

## Dependencies and Integration Points
The module depends on `kvproto` raft command and lock messages, `uuid`, TiKV metrics, `MustConsumeVec` callback safety, store config, and apply notification helpers. It integrates with peer FSM role changes through `clear_uncommitted_on_role_change`, with region removal through `clear_all(Some(region_id))`, and with raft Ready read states through the leader/replica advance methods.

## Risks and Edge Cases
The absolute-offset scheme depends on accurate `handled_cnt` updates in every pop/push-front path. Incorrect role-change sequencing could leave stale contexts, which is why tests cover leader-to-follower and retake-leadership flows. `ReadIndexContext::parse` trusts encoded lengths enough to slice buffers; malformed internal raft contexts can panic or error depending on the field. The `READ_INDEX_SAFE_TS_FLAG` length is encoded as an eight-byte number containing the fixed u64 length, which is unusual and must remain compatible with the parser.

## Test Signals
Tests validate backward-compatible UUID-only context parsing, context serde for request/lock/safe-ts fields, role changes from follower to leader to follower, leadership retake after an unhandled ready read, and out-of-order replica advancement. These tests target the key invariants around context-map cleanup and queue offsets.
