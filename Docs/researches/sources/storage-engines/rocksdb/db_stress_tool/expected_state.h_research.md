# sources/storage-engines/rocksdb/db_stress_tool/expected_state.h

## Purpose
`expected_state.h` defines the abstraction for tracking db_stress expected values across keys and column families. It separates the logical API for expected-value mutation from the storage backing, allowing in-memory state for normal runs and file-backed state for crash/recovery tests.

## Important APIs, types, and functions
`ExpectedState` exposes `Open()`, `ClearColumnFamily()`, persisted-seqno accessors, `PreparePut()`, `PrepareDelete()`, `PrepareSingleDelete()`, `PrepareDeleteRange()`, `Get()`, `Exists()`, and sync methods. `FileExpectedState` adds mmap-backed state and persisted-seqno files. `AnonExpectedState` allocates atomics in memory. `ExpectedStateManager` wraps the latest state and exposes the same mutation APIs plus history APIs `SaveAtAndAfter()`, `HasHistory()`, and `Restore()`. `FileExpectedStateManager` persists history in a directory; `AnonExpectedStateManager` reports history unsupported.

## Control flow
Callers interact through `ExpectedStateManager`. The manager opens a concrete latest state, forwards per-key operations, and delegates save/restore behavior to the concrete subclass. Prepare APIs return `PendingExpectedValue` tokens so the caller can bracket DB writes: mark expected state pending before the DB write and commit/rollback the token after knowing the write outcome.

## State and persistence behavior
State layout is a flat array indexed by `cf * max_key + key`. Each cell is an atomic `uint32_t` encoding the value base, deletion counter, pending-write bit, pending-delete bit, and deleted bit. `persisted_seqno_` is tracked separately. File-backed state stores the array and persisted sequence number in mmap files; anonymous state uses heap allocations. File manager constants define the on-disk naming scheme: `LATEST.state`, `<seqno>.state`, `<seqno>.trace`, `PERSIST.seqno`, and temp-file wrappers.

## Dependencies and integration points
The header includes RocksDB DB, Env, FileSystem, dbformat sequence-number types, file utilities, `ExpectedValue`, and string utilities. It is used by stress-test operation implementations that need expected-state tracking and by crash-test paths that need history restoration.

## Risks and test signals
Thread-safety is intentionally external: most mutation methods require callers to lock relevant keys or entire column families. Incorrect locking can produce expected-state races independent of DB correctness. The file-backed implementation assumes the mmap file sizes match exactly and that atomics are valid over mapped storage. Tests should verify prepare-token lifecycle assertions, CF clearing, range deletes, persisted sequence monotonicity, fresh anonymous open, file-backed reopen, and unsupported history methods on anonymous managers.
