# sources/storage-engines/pebble/wal/reader_test.go

## Purpose
Datadriven and regression tests for Pebble WAL logical listing, virtual segment replay, duplicate suppression, tail-corruption handling, and logical WAL copy.

## Important APIs, Types, And Functions
`TestList` exercises `Scan`, `FileAccumulator`, `ParseLogFilename`, and safe formatting. `TestReader` builds real record log files with `record.LogWriter`, then reads them through `LogicalLog.OpenForRead` and `virtualWALReader`. `TestCopyClosesWriterOnError` verifies `Copy` closes destination resources after corruption errors.

## Control Flow
The `list` test maintains named in-memory filesystems, accepts `touch`, `reset`, and `list` commands, and prints logical WALs. The reader test supports `define`, `copy`, and `read` commands. `define` writes fake batch records, garbage bytes, recycled files, corrupt tails, synced records, and crash-cloned unclean logs. `read` scans WALs, optionally injects nonexistent segment metadata, and prints every `NextRecord` result plus decoded batch headers. `copy` invokes `Copy` into a target directory with a requested visible sequence number.

## State And Persistence Behavior
Tests use crashable and logging `MemFS` implementations to model durable directory sync, file creation, recycling, unsynced data loss, and open file tracking. Batch sequence numbers and counts are encoded into record payloads so reader deduplication and LogData-only skip rules are observable.

## Dependencies And Integration Points
Uses `datadriven`, Pebble `batchrepr`, `record`, `vfs`, `vfstest.WithOpenFileTracking`, `datadrivenutil`, leak tests, and testify assertions. The tests bind WAL package behavior to lower record-layer semantics.

## Risks And Edge Cases
Important cases are stale readers after `NextRecord`, unclean WAL tails from crash/recycle, duplicated records across segments, records too short for batch headers, LogNameIndex gaps, missing physical segment files, and resource cleanup when `Copy` fails before the log writer closes normally.

## Test Signals
The datadriven output shows exact offsets, physical file paths, record contents, parsed headers, and errors. The regression test fails if open destination handles remain after `Copy` returns an expected corruption error.
