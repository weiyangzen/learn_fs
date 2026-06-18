# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/replica.rs

## Purpose
Implements follower/replica read-index support for raftstore-v2, including retrying lost read-index requests and responding to replica reads once follower apply progress is safe.

## Important APIs, Types, And Functions
`Peer::retry_pending_reads` periodically retries pending follower read-index requests. `read_index_follower` proposes a follower read-index through raft. `respond_replica_read` returns successful replica-read or read-index responses. `respond_replica_read_error` reports the same error to every command batched in a pending read.

## Control Flow
Follower read-index first checks that a leader is known. It extracts any embedded read-index request payload, calls `propose_read_index`, stores a `ReadIndexRequest` in the pending queue, and marks ready. Retry logic checks that the peer is still a follower, pending reads need retry, and `pre_read_index` still permits reads; it then reissues raft `read_index` with the existing request context. Responses are emitted only after `query/mod.rs` determines that the follower has applied through the returned read index.

## State And Persistence Behavior
The file manages in-memory pending-read state only. Read-index itself is a raft protocol operation and does not persist local durable state directly. Tracker metrics record wait time from proposal to confirmation.

## Dependencies And Integration Points
Depends on raft leader id, `ReadIndexContext`, pending read queue, `propose_read_index`, `ReadResponse`, query channels, stale request notification, and configuration retry thresholds. It is called from query tick/ready handling in `ready/mod.rs` and `query/mod.rs`.

## Risks And Edge Cases
If no leader is known, reads fail with `NotLeader`. Read-index responses can be lost, so retry is required to avoid permanently queued follower reads. Lock information returned by the leader is converted into a read-index response error. Requests that were proposed while the peer was leader but complete after it becomes follower are notified stale unless they explicitly allow replica read.

## Test Signals
No local unit tests are present. Signals include read-index pending metrics, retry logs, `read_index_no_leader` metric, lock-response handling, and integration tests for follower reads under lost responses or apply lag.
