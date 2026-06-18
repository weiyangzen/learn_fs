# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_trace_apply.rs

## Purpose
This integration test validates trace-apply recovery for tablet data after restart, especially with RocksDB WAL disabled. It ensures unflushed raft-applied writes are replayed from raft/apply traces and that already flushed data does not cause redundant recovery writes.

## Important APIs, Types, and Functions
- `count_file()`, `count_sst()`, and `count_info_log()` inspect tablet directory files.
- `test_data_recovery()` writes 100 keys into each data CF with different flush patterns: default CF unflushed, write CF half flushed, lock CF fully flushed.
- It uses `avoid_flush_during_shutdown` to prevent shutdown flushes from masking recovery behavior.

## Control Flow
The test records initial LOG count, writes default/write/lock CF data, flushes selected CFs, verifies all data through a stale snapshot, disables shutdown flush, restarts, writes another key, and verifies all original data recovered. It checks LOG and SST counts, flushes all CFs, checks only expected recovery memtables created new SSTs, restarts again, verifies data is immediately readable, flushes again, and confirms no extra SSTs were produced.

## State and Persistence Behavior
This is a direct persistence test for tablet data, raft apply trace, RocksDB SST creation, WAL skipping, and recovery replay. Because WAL is disabled, unflushed data must come back through raftstore-v2 recovery logic rather than RocksDB WAL.

## Dependencies and Integration Points
It depends on tablet registry paths, RocksDB file layout, CF flush APIs, snapshots, `SimpleWriteEncoder`, router writes, `DATA_CFS`, and `RAFT_INIT_LOG_INDEX`.

## Risks and Edge Cases
- Unflushed applied writes must not be lost across restart.
- Recovery must be CF-aware and avoid rewriting already flushed ranges.
- Disabling shutdown flush is necessary to expose recovery rather than normal RocksDB persistence.
- File-count assertions are sensitive to RocksDB behavior changes.

## Test Signals
Signals include exact LOG counts after restarts, exact SST counts after controlled flushes, and full key/value verification across all data CFs before and after restarts.
