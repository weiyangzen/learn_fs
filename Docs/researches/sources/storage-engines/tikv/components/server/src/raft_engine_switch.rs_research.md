## sources/storage-engines/tikv/components/server/src/raft_engine_switch.rs

Purpose: migrates raft log/state data between RocksDB raftdb and raft-log-engine formats.

Important APIs/types/functions: `dump_raftdb_to_raft_engine`, `dump_raft_engine_to_raftdb`, `run_dump_raftdb_worker`, `run_dump_raft_engine_worker`, and emptiness checks. `BATCH_THRESHOLD` limits log batch size.

Control flow: public dump functions assert the target is empty, spawn worker threads, scan source raft groups/region ids, send ids over a channel, wait for workers, then sync the target. RocksDB-to-raft-engine workers scan raft key ranges, decode log entries/state, append batches, and consume periodically. Reverse workers fetch raft state and entries in chunks and consume Rocks batches.

State/persistence: directly writes target engine data and syncs it. Counts total transferred bytes with an atomic counter. Source engines are read-only during migration.

Dependencies/integration: used by `ConfiguredRaftEngine` implementations in `common.rs` during raft engine switching. Depends on RocksEngine, RaftLogEngine, raft key encoding, protobuf merge, raft entries, and engine traits.

Risks: uses assertions/panics for non-empty targets and decode errors; assumes raftdb scan ordering sees entries before raft state; concurrent migration thread count must be nonzero for progress; migration is a critical on-disk operation.

Test signals: tests create temporary engines, write raft batches for regions 1/5/15, migrate both directions, and verify state/entries with and without separate raftdb WAL.
