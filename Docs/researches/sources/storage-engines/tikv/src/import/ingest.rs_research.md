# sources/storage-engines/tikv/src/import/ingest.rs

## Purpose
Contains shared ingest orchestration for SST import RPCs: request suspension, conflict latching, write-stall admission, snapshot/term acquisition, file existence checks, and raft-backed ingest writes.

## Important APIs, Types, and Functions
`IngestLatch` serializes in-flight SST ingestion per `(cf_name, path)`. `SuspendDeadline` uses an `AtomicU64` physical timestamp to reject import requests temporarily. `check_write_stall` detects region/tablet availability and write-CF ingest slowdown. `async_snapshot` obtains an engine snapshot and converts storage errors to region protobuf errors. `ingest_files_impl` validates API version, obtains snapshot term, checks SST files exist, and sends `Modify::Ingest` writes. Public `ingest` performs suspension/admission/latch logic then delegates.

## Control Flow
`ingest` first rejects if suspended. Under `ingest_admission_guard`, it checks write stall and attempts to acquire all SST latches. Partial latch acquisition is rolled back and returns file conflict. `ingest_files_impl` checks importer API version, awaits raft snapshot, verifies local SST files after snapshot to avoid retry races, sets the request term from snapshot extension, and issues `engine.async_write`; `wait_write` maps the write stream result to a response error if needed. Latches are released after the async ingest attempt.

## State and Persistence Behavior
`IngestLatch` and `SuspendDeadline` are in-memory service state. Successful ingestion persists SST contents through raft/engine `Modify::Ingest`. The importer controls file existence and API-version metadata. Metrics are incremented through `pb_error_inc` and importer error counters.

## Dependencies and Integration Points
Depends on `SstImporter`, raftstore v2 `StoreMeta`, local tablets, TiKV engine async snapshot/write APIs, importer protobufs, and `raft_writer::wait_write`. Called by both single-file `ingest` and `multi_ingest` RPC handlers in `sst_service.rs`.

## Risks and Edge Cases
Latch release must happen after all paths, and this file handles that manually after await. Write-stall rejection differs between raftstore v1 and v2/import mode. File existence after snapshot intentionally returns stale command to make retries safe, but can confuse clients if files are externally removed. `acquire_lock(meta).unwrap_or(false)` suppresses path conversion errors into conflict-like behavior.

## Test Signals
No direct tests in this file. Behavior is exercised indirectly by import service integration tests elsewhere and by raft writer tests for `wait_write`.
