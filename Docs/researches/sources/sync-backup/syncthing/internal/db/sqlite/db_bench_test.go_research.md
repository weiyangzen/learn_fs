# sources/sync-backup/syncthing/internal/db/sqlite/db_bench_test.go

## Purpose
This file contains performance benchmarks and long-running size/drop tests for the SQLite database implementation.

## Important APIs, Control Flow, And State
`BenchmarkUpdate` opens a temporary DB, preloads increasingly large local datasets, logs file/block throughput, and runs sub-benchmarks for inserting local files, replacing blocks, replacing same files, inserting remote files, global lookups, sequence iteration, block hash lookups, device sequence reads, remote need iteration, and local need ordering. It uses generated `protocol.FileInfo` values and reports custom `files/s` and `blocks/s` metrics. `TestBenchmarkDropAllRemote` is a slow opt-in test gated by `LONG_TEST`, fills local and remote state, and times `DropAllFiles` for a remote device. `TestBenchmarkSizeManyFilesRemotes` is another opt-in long test that simulates 100k files shared by 31 devices and logs database size.

## State And Persistence
The tests create temporary SQLite databases and folder databases, then fill them with synthetic file, block, version-vector, and device state. They close and measure on-disk directories where needed.

## Dependencies And Integration Points
It depends on the SQLite `Open` path, test data helpers such as `genFile`/`genBlocks` and `folderID` from package tests, protocol/config types, `timeutil`, `osutil.DirSize`, and random string generation.

## Risks And Test Signals
These are performance signals, not correctness assertions for normal CI. The benchmark grows the dataset up to 200k local files and can be expensive. Long tests require `LONG_TEST` and are skipped in short/default runs. They are useful for detecting update/index/query regressions, block index growth, remote-device scaling costs, and database size changes.
