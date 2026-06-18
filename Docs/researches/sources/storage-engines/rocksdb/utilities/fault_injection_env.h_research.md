# sources/storage-engines/rocksdb/utilities/fault_injection_env.h

## Purpose
This header declares the legacy `FaultInjectionTestEnv` and its wrapped file/directory types for testing crash and filesystem-failure behavior.

## Important APIs, Types, and Functions
`FileState` records filename, current position, last sync position, and last flush position, and exposes unsynced-data drop helpers. `TestRandomAccessFile`, `TestWritableFile`, `TestRandomRWFile`, and `TestDirectory` wrap legacy Env file objects. `FaultInjectionTestEnv` derives from `EnvWrapper` and overrides key Env operations. It exposes `DropFileData`, `DropUnsyncedFileData`, `DropRandomUnsyncedFileData`, `DeleteFilesCreatedAfterLastDirSync`, `ResetState`, `UntrackFile`, `SyncDir`, filesystem active toggles, `AssertNoOpenFile`, and `GetError`.

## Control Flow
The declared wrappers gate operations on `IsFilesystemActive`, update tracked state on append/sync/close, and let the env simulate crash recovery by truncating unsynced bytes or deleting unsynced directory entries. `SetFilesystemActive` freezes state updates and causes subsequent operations to return a configured error.

## State and Persistence Behavior
The env stores file states, open managed files, unsynced directory entries, active flag, and error status under a mutex. It mutates real files only when drop/delete helpers or forwarded Env calls run.

## Dependencies and Integration Points
It depends on RocksDB Env APIs, filename types, and mutex utilities. It is a test utility for DB recovery, WAL, checkpoint, and durability scenarios using legacy Env interfaces.

## Risks and Edge Cases
The header exposes many mutable controls, so tests must reset state carefully between scenarios. The model tracks files created through this wrapper; externally created files may not be eligible for dropping. `GetFreeSpace` has a Windows macro workaround and reports zero free space when inactive with `NoSpace`.

## Test Signals
Compile and behavior tests should exercise all wrapper types, inactive status propagation, no-space free-space behavior, unsynced truncation, random truncation, directory sync tracking, rename/link state propagation, and open-file assertions.
