# sources/storage-engines/rocksdb/db_stress_tool/db_stress_listener.cc

## Purpose

`db_stress_listener.cc` implements the non-inline parts of `DbStressListener` and `UniqueIdVerifier`. Together they make the stress test observe RocksDB event callbacks and verify that every generated SST extended unique ID remains unique across the current run and prior runs that share the same DB or expected-values directory.

## Important APIs, Types, and Functions

- `DbStressListener::DbStressListener(...)` captures DB identity, DB paths, column-family descriptors, `SharedState`, and optional `FaultInjectionTestFS`; it chooses the unique-ID bookkeeping directory from `expected_values_dir` or the DB directory.
- `UniqueIdVerifier::UniqueIdVerifier()` creates `dir/.unique_ids`, loads old 24-byte IDs through a temporary rename/copy sequence, and verifies prior partial IDs.
- `UniqueIdVerifier::~UniqueIdVerifier()` closes the writer while temporarily clearing thread operation tracking.
- `VerifyNoWrite()` decodes an 8-byte subsequence from a 24-byte ID and asserts uniqueness in memory.
- `Verify()` appends and flushes a new ID, then checks uniqueness under a mutex.
- `DbStressListener::VerifyTableFileUniqueId()` extracts extended unique IDs from `TableProperties`.

## Control Flow and State Behavior

Construction initializes listener fields and then the verifier. The verifier uses `Env::Default()->GetFileSystem()` for its bookkeeping file even when the tested DB uses a remote filesystem. It creates the directory, renames an existing `.unique_ids` to `.tmp`, reads fixed-width records, clears corrupt partial trailing records, creates a fresh file, copies old content back with fsync, and deletes the temp file.

On new table-file events, header callbacks call `VerifyTableFileUniqueId()`. `Verify()` appends before checking so a just-seen ID is persisted for future executions even if a duplicate assertion terminates the process.

Persistent state is limited to `.unique_ids` under the expected-values directory or DB directory.

## Dependencies and Integration Points

The implementation uses `db_stress_listener.h`, `db_stress_test_base.h`, `file/file_util.h`, `rocksdb/file_system.h`, `util/coding_lean.h`, `WritableFileWriter`, `Env::Default()`, `CopyFile`, `Random`, `ThreadStatusUtil`, `TableProperties`, and `GetExtendedUniqueIdFromTableProperties()`. It is installed through `db_stress_test_base.cc` via the listener defined in the header.

## Risks and Edge Cases

The `.unique_ids` file format is append-only binary records. Partial trailing records are treated as corrupt process-crash residue and cause previous uniqueness evidence to be cleared. Only one random 64-bit slice of each 24-byte ID is tracked, so the uniqueness check is probabilistic. The verifier stops after about 4.29 million IDs to keep natural collision risk bounded.

Most failures assert or exit, which is suitable for a stress binary but not recoverable. The local filesystem choice can fail independently of the DB filesystem.

## Test Signals

Signals include `(Re-)verified N unique IDs`, no duplicate-ID assertions, successful flush/compaction/external-ingestion events that call `VerifyTableFileUniqueId()`, and `.unique_ids` persistence across crash-test invocations.
