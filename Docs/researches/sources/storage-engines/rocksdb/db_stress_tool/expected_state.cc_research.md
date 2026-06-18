# sources/storage-engines/rocksdb/db_stress_tool/expected_state.cc

## Purpose
`expected_state.cc` implements the expected-value state store used by `db_stress` to compare logical DB contents against what the stress workload believes should exist. It supports an anonymous in-memory mode and a file-backed, mmap-based mode with crash-recovery history. The file-backed manager can snapshot expected values at a DB sequence number, trace later writes, and restore expected values after recovery by replaying traced write batches.

## Important APIs, types, and functions
Core implementations include `ExpectedState::{PreparePut,PrepareDelete,PrepareDeleteRange,SyncPut,SyncDelete,Reset}`, `FileExpectedState::Open()`, `AnonExpectedState::Open()`, `FileExpectedStateManager::{Open,SaveAtAndAfter,HasHistory,Restore,Clean}`, and `AnonExpectedStateManager::Open()`. The internal `ExpectedStateTraceRecordHandler` implements both `TraceRecord::Handler` and `WriteBatch::Handler` to replay traced puts, timed puts, entities, deletes, single deletes, ranges, merges, blob index writes, and prepared-transaction markers.

## Control flow
`ExpectedState` stores one atomic `uint32_t` per `(cf,key)` plus an atomic persisted sequence number. Prepare methods load the current value, derive original/pending/final `ExpectedValue` states, precommit the pending state with a release fence, and return a `PendingExpectedValue` that must later commit or roll back. Sync methods directly force expected values during recovery or scan. `FileExpectedState::Open()` optionally creates zeroed files, mmaps state and persisted-seqno files, and resets new state to deleted. `FileExpectedStateManager::Open()` discovers prior `<seqno>.state` files, creates missing empty trace files for interrupted saves, cleans stale temps, creates `LATEST.state`/`PERSIST.seqno` if absent, then opens the latest mmap.

`SaveAtAndAfter()` copies `LATEST.state` to an atomic `<seqno>.state`, starts an unbuffered trace at `<seqno>.trace` with write order preserved, updates `saved_seqno_`, and removes the previous history pair. `Restore()` computes `db->GetLatestSequenceNumber() - saved_seqno_`, copies the saved state to a temp latest file, replays trace records until that many write operations have been applied, atomically renames the temp latest, reopens it, and deletes old state/trace files. Trace replay tolerates corrupt tail records only after enough writes have already been applied.

## State and persistence behavior
File-backed state uses `LATEST.state`, `PERSIST.seqno`, `<seqno>.state`, `<seqno>.trace`, and hidden `.<name>.tmp` files. Atomic rename is used for state publication. Traces must be an ordered superset of writes that can survive recovery: missing entries are fatal, extra suffix entries are allowed. Prepared transaction replay buffers writes between prepare markers, applies them on commit, and drops them on rollback. `Clean()` removes temp files and stale histories older than the selected saved sequence.

## Dependencies and integration points
This file depends on `ExpectedValue`, DB sequence numbers, file utilities, Env/FileSystem APIs, trace reader/writer/replayer APIs, wide-column serialization helpers, timestamp stripping helpers, `db_stress_common` key/value helpers, and `SharedState` flags for debug behavior. It is the persistence backing for crash-test expected values used by broader db_stress workloads.

## Risks and test signals
The main risks are replay/count mismatches, trace truncation, key parsing failures, timestamp stripping errors, and inconsistency between logical write effects and expected-value updates. Blob direct-write replay derives the next value base because traces store blob indexes rather than original values. DeleteRange replay treats the operation as one write op while mutating many expected keys. Debug counters for key decode failures, roundtrip mismatches, focus-key hits, emitted logs, and suppressed logs are useful test signals. Crash tests should exercise interrupted open/save/restore, prepared transaction commit/rollback, wide entities, timed puts, merges, blob indexes, and corrupted trace tails.
