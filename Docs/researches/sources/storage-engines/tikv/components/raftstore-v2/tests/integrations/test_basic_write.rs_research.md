# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_basic_write.rs

## Purpose
This integration test file validates the basic raftstore-v2 simple-write path, request validation, follower rejection, put/delete behavior, stale snapshots, and WAL-skipping behavior for tablet writes.

## Important APIs, Types, and Functions
- `test_basic_write()` sends a valid simple write, then checks store mismatch, peer mismatch, epoch mismatch, stale term, entry-too-large rejection, and not-leader rejection after a higher-term heartbeat.
- `test_put_delete()` writes a key, reads it through stale snapshot, deletes it, reads absence, and checks WAL files are empty.
- The tests use `SimpleWriteEncoder`, `PeerMsg::simple_write`, router subscriptions, `new_peer`, epoch constants, and `check_skip_wal()`.

## Control Flow
The tests wait for region 2 to apply to current term, build request headers from debug info, and send simple-write messages through the router. Subscription futures verify proposed, committed, and final response phases. Invalid headers are cloned and mutated from a known-good header. The follower path is triggered by sending a crafted heartbeat from a higher-term peer to step down the local peer.

## State and Persistence Behavior
Successful writes mutate the tablet default CF and are visible through snapshots. Deletes remove data from the same CF. `check_skip_wal()` verifies the underlying tablet RocksDB uses empty WAL files for these raft-applied writes, implying durability comes from raft log/apply trace rather than RocksDB WAL.

## Dependencies and Integration Points
It depends on the shared cluster harness, raftstore store epoch constants, engine snapshot reads, raft messages, and raftstore-v2 router/simple-write APIs.

## Risks and Edge Cases
- Request validation must reject wrong store/peer/epoch/term before mutation.
- Large entries must be rejected before raft log append.
- A peer stepped down by a higher-term heartbeat must reject writes as not leader.
- WAL skipping is safe only if raft/apply recovery remains correct.

## Test Signals
Signals include successful proposed/committed/result futures, specific error fields (`store_not_match`, `epoch_not_match`, `stale_command`, `raft_entry_too_large`, `not_leader`), snapshot key presence/absence, and empty WAL file lengths.
