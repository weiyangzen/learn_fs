# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_read.rs

## Purpose
This file validates raftstore-v2 read-query behavior: read-index execution and lease skipping, snap requests without explicit read index, rejection of write commands through query path, invalid snapshot request parameters, and local snapshot retry/lease behavior.

## Important APIs, Types, and Functions
- `test_read_index()` configures a short leader lease, issues snap+read-index queries, observes read-index value 6 after lease expiry and 0 while lease is valid or renewed by write.
- `test_snap_without_read_index()` confirms plain snap reads can use lease, while `read_quorum` forces read-index.
- `test_query_with_write_cmd()` sends write command types through query and expects error responses, not read results.
- `test_snap_with_invalid_parameter()` checks store id, peer id, stale term, stale-read flag, and invalid epoch rejection.
- `test_local_read()` uses `router.snapshot()` directly, then query returns read-index 0 because snapshot retry renewed the lease.

## Control Flow
The tests create `RaftCmdRequest` values with `CmdType::Snap`, optional `read_index`, and header flags. They sleep past configured lease durations to force read-index. Writes use `SimpleWriteEncoder` and `PeerMsg::simple_write` to renew leases. Invalid cases mutate a known-good request and inspect `QueryResult`.

## State and Persistence Behavior
The tests primarily observe raft read state and leader lease state, not persistent storage. The write in `test_read_index()` mutates tablet data only to renew the leader lease.

## Dependencies and Integration Points
They depend on cluster query/snapshot helpers, raft command protobufs, `WriteBatchFlags`, router read APIs, and raftstore-v2 lease/read-index code.

## Risks and Edge Cases
- Read-index should be skipped only under valid lease unless `read_quorum` is set.
- Write commands must never execute through query path.
- Stale-read flags are invalid for this snap query path.
- Direct local snapshot retries can renew lease, affecting later read-index expectations.

## Test Signals
Signals include exact read-index values (`6` or `0` in the single-node setup), missing read result for write commands, and response-header errors for invalid parameters.
