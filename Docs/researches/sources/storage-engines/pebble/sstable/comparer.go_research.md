# sources/storage-engines/pebble/sstable/comparer.go

## Purpose
Re-exports comparer and merger-related base types from the public `sstable` package.

## Important APIs, Types, and Functions
- Type aliases: `Compare`, `Equal`, `AbbreviatedKey`, `Separator`, `Successor`, `Split`, `Comparer`, and `Merger`.
- Variable alias: `DefaultComparer`.

## Control Flow
There is no runtime control flow beyond alias resolution at compile time.

## State and Persistence Behavior
No state is persisted. The aliases shape public API compatibility and allow callers to configure reader/writer ordering without importing internal base packages.

## Dependencies and Integration Points
Depends on `internal/base`. Used by `ReaderOptions`, `WriterOptions`, external SSTable construction, and debugging tools.

## Risks and Edge Cases
Because these are aliases, changes in `base` type definitions propagate directly to the public `sstable` API. Comparer consistency remains essential for reading and writing SSTables.

## Test Signals
No direct tests in this file; exercised by all reader/writer tests that use `sstable.Comparer` or `DefaultComparer`.
