# sources/storage-engines/leveldb/db/fault_injection_test.cc

## Purpose
This suite simulates crash-like loss of unsynced file data or unsynced newly-created files, validating LevelDB recovery across sync boundaries with and without log reuse.

## Important APIs, Types, And Functions
`FileState` tracks file position, last sync, and last flush. `TestWritableFile` wraps `WritableFile` to report appends, flushes, syncs, close, and parent directory sync. `FaultInjectionTestEnv` wraps Env operations, tracks file states and files created since the last directory sync, and can truncate unsynced data or remove unsynced files. `FaultInjectionTest` supplies `Build`, `Verify`, `OpenDB`, `CloseDB`, `DeleteAllData`, `ResetDBState`, and partial/no-write fault scenarios.

## Control Flow
Each test opens a DB under the wrapper env, repeatedly writes and compacts a pre-sync population, writes a post-sync population, simulates filesystem inactivity, closes the DB, drops unsynced state by truncating data or deleting unsynced new files, reopens, and verifies which key ranges should survive. It runs both `reuse_logs=false` and `reuse_logs=true`.

## State And Persistence Behavior
The wrapper models durable state as data that has reached `Sync()` and directory entries whose parent directory has been synced. `DropUnsyncedData` truncates files to their last synced position. `RemoveFilesCreatedAfterLastDirSync` deletes new files whose directory entries were not synced. The test assumes actual directory sync is not needed for the test environment and records it logically.

## Dependencies And Integration Points
It integrates `DBImpl`, Env wrappers, writable file lifecycle, file naming, log format, version set, table files, cache, write batches, mutex annotations, and random test data. It validates DBImpl's ordering of table/log/manifest/directory syncs.

## Risks And Edge Cases
This is a model of crash behavior, not a perfect filesystem simulator. It uses truncation via default Env and tracks only files opened through the wrapper. Expected errors for post-sync ranges are broad: a missing value is treated as acceptable when loss is expected.

## Test Signals
Passing indicates pre-sync data remains readable after simulated faults, post-sync unsynced data can be lost without corrupting the DB, and log reuse does not violate recovery guarantees.
