# sources/storage-engines/tikv/tests/integrations/storage/test_raftkv.rs

## Purpose
This integration test validates the lower-level raft-backed `kv::Engine` interface: snapshots, writes, deletes, CF access, cursor seek behavior, replica reads, read-index behavior, in-memory lock checking, and write prechecks on followers or isolated leaders.

## Important APIs, Types, and Functions
The file uses `Engine`, `SnapContext`, `WriteData`, `Modify`, `Cursor`, `IterOptions`, `CfStatistics`, and helpers such as `must_put`, `assert_has`, `assert_seek`, `near_seek`, `cf`, `empty_write`, and `wrong_context`. It also uses raftstore packet filters and `read_index_on_peer`.

## Control Flow
`test_raftkv` starts a one-node server cluster, obtains the leader storage, builds a region `Context`, and runs basic get/put, batch write, seek, near-seek, CF, empty-write, and wrong-context checks. Multi-node tests validate leader lease reads after isolating the leader, follower read-index responses, replica snapshot reads with `replica_read`, catch-up after follower restart, memory-lock detection for replica reads, not-leader read-index errors when heartbeats/appends are delayed, and `precheck_write_with_ctx` failures on followers or isolated leaders.

## State, Persistence, and Dependencies
State includes raft region membership, current leader, local storage handles, RocksDB CF data, memory lock entries in the concurrency manager, and simulator packet filters. Dependencies include `kvproto::Context`, raft message types, `test_raftstore`, and TiKV storage `kv` abstractions.

## Integration Points, Risks, and Test Signals
The file checks the boundary between raftstore leadership/read-index semantics and storage snapshots. It has strong signals for encoded key ordering, CF isolation, lock error equality, and not-leader headers. Risks include sleeps for election/catch-up and reliance on exact simulator timing.
