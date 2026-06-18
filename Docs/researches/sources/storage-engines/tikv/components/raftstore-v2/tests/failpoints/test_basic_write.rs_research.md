# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_basic_write.rs

## Purpose
This failpoint test file validates raftstore-v2 write apply robustness under injected apply failures and delete-range persistence corner cases. It focuses on write-batch rollback/isolation and ensuring delete-range commands do not break recovery or flushed-index advancement.

## Important APIs, Types, and Functions
- `test_write_batch_rollback()` pauses `APPLY_COMMITTED_ENTRIES`, injects `APPLY_PUT` failures, and checks that failed and successful simple writes in the same apply batch remain isolated.
- `test_delete_range()` writes data to default/write CFs, applies a default-CF delete range while suppressing apply-trace persistence, restarts, and verifies delete-range replay.
- `test_delete_range_does_not_block_flushed_index()` verifies that a file-level delete range against default CF does not prevent later flushed-index advancement for writes in another CF.
- The tests use `SimpleWriteEncoder`, `PeerMsg::simple_write`, `router.stale_snapshot`, RocksDB flush/compaction helpers, and raft-engine flushed-index reads.

## Control Flow
The write-batch test queues two committed writes while apply is paused, injects one failing put, resumes apply, and asserts only the failing command returns an aborted error and only its key is absent. It repeats the sequence to confirm rollback after an initialized batch. The delete-range tests force data into SSTs, apply range deletion, manipulate apply-trace failpoints, close/remove tablets, restart the cluster, and inspect snapshots and raft-engine flushed indexes.

## State and Persistence Behavior
The tests intentionally exercise WAL-disabled tablet writes, write-batch rollback, CF-specific flush state, apply-trace persistence, and raft-engine flushed-index records. They simulate crash/restart windows by disabling apply-trace persistence and forcing tablet registry removal before restart.

## Dependencies and Integration Points
They depend on the integration `Cluster`, raftstore-v2 router subscriptions for proposed/committed/result phases, `engine_traits` CF operations, manual compaction, and raft-engine read-only APIs. The failpoints target apply code paths outside this file.

## Risks and Edge Cases
- A stale write batch can leak failed mutations into later successful commands; this file is specifically guarding that.
- Delete-range by file can produce no memtable writes for empty CFs; flushed-index logic must not wait forever for nonexistent flush work.
- Restart recovery must replay delete-range commands even when apply trace was not persisted.

## Test Signals
Strong assertions include aborted error messages, key absence/presence across snapshots, WAL/tablet restart behavior, and monotonically advancing raft-engine flushed indexes after cross-CF writes.
