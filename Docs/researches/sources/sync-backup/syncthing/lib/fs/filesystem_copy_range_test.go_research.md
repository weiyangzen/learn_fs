# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_test.go

## Purpose
Validates all registered copy-range implementations across offset, size, alignment, sparse, and error cases.

## Important APIs, Types, and Functions
Global `testCases` describe source/destination sizes, offsets, starting seek positions, copy size, expected destination size, and per-method expected errors. `TestCopyRange` runs each registered method.

## Control Flow
Tests create random source/destination files, set initial seek positions, unwrap to `basicFile`, call each implementation, then verify original seek positions, destination size, copied bytes, and untouched or zero-filled regions.

## State and Persistence Behavior
Creates temp directories and files, optionally under paths from `STFSTESTPATH` to test specific filesystems. Destination files are mutated by each copy operation.

## Dependencies and Integration Points
Uses `copyRangeMethods`, `unwrap`, `NewFilesystem(FilesystemTypeBasic)`, `io`, `syscall`, and random data.

## Risks
Some hardware/filesystem methods may be unsupported and are skipped when returning unsupported. Expected errors differ by method and platform, so the table must track syscall behavior carefully.

## Test Signals
Strong signal for copy correctness, non-corruption, seek-position preservation, sparse expansion, and graceful unsupported handling.
