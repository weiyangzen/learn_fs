# sources/storage-engines/foundationdb/fdbserver/workloads/StorageServerCheckpointRestoreTest.cpp

## Purpose
`SSCheckpointRestoreWorkload` is a single-client simulation workload that exercises storage-server checkpoint creation, checkpoint metadata lookup, checkpoint fetch to the local filesystem, and restoration into a standalone RocksDB key-value store. It validates that a key range restored from fetched checkpoint files matches the same range read from the live database.

## Important APIs, Types, and Functions
The file defines a local `printValue()` helper and `SSCheckpointRestoreWorkload : TestWorkload`, registered by `WorkloadFactory<SSCheckpointRestoreWorkload>`. Key methods are `validationFailed()`, `start()`, `_start()`, `readAndVerify()`, `writeAndVerify()`, `check()`, and `disableFailureInjectionWorkloads()`. It depends on checkpoint APIs such as `createCheckpoint()`, `getCheckpointMetaData()`, `fetchCheckpoint()`, `CheckpointMetaData`, `CheckpointFormat`, `newDataMoveId()`, data movement metadata types, `IKeyValueStore::restore()`, and `keyValueStoreRocksDB()`.

## Control Flow
Only client 0 runs the workload. `_start()` disables DD, writes and verifies `TestKey`, creates a checkpoint for `[TestKey, TestKey0)`, retries metadata lookup until it succeeds, erases and recreates a local `checkpoints` directory, fetches each checkpoint record, restores those fetched files into a fresh RocksDB test store, reads the target range from both the live database and restored store, asserts size and key-value equality, disposes the store, and re-enables DD. Transactional loops use `tr.onError()` and some operations use `timeoutError()` to avoid indefinite read/write waits.

## State and Persistence Behavior
Persistent cluster state is a single test key/value plus system metadata produced by checkpoint creation. External state is written under the process working directory in `checkpoints` and `rocksdb-kvstore-test-db`; both are erased before use. The restored KVS is local process state and is disposed after comparison. DD mode is modified through `setDDMode(cx, 0)` and later `setDDMode(cx, 1)`, so failures before the final reset can affect later simulation behavior.

## Dependencies and Integration Points
The workload integrates with the tester framework, Native API transactions, system-key-aware management APIs, data distribution mode control, server checkpoint internals, MoveKeys data movement IDs, RocksDB storage-engine creation, and Flow platform filesystem helpers. It disables `RandomMoveKeys` and `Attrition` because concurrent shard movement or process attrition would race with checkpoint/restore validation.

## Risks and Edge Cases
The test uses `ASSERT` for equality and restore preconditions, so mismatches crash the workload rather than only flipping `pass`. `TestRestoreCheckpointError` logs restore failure but does not immediately fail before reading from the store, which can turn restore errors into later assertions. The local directories are fixed relative paths and can conflict with other local tests sharing a working directory. DD mode is restored only on the normal path. The range currently covers a single key, so multi-key and empty-range checkpoint restore coverage is narrow.

## Test Signals
Trace events include `TestCheckpointRestoreBegin`, `TestCreatingCheckpoint`, `TestCheckpointCreated`, `TestCheckpointFetched`, `TestFetchCheckpointError`, `TestRestoreCheckpointError`, and `TestFailed`. `check()` returns the `pass` flag, although the strongest signals are assertions during checkpoint fetch/restore/range comparison.
