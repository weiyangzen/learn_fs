# sources/storage-engines/pebble/sstable/colblk_writer_test.go

## Purpose
Datadriven tests for building and inspecting columnar-format SSTables with `RawColumnWriter`.

## Important APIs, Types, and Functions
- `TestColumnarWriter` walks `testdata/columnar_writer`.
- `build` command constructs a v5, no-compression writer using `testkeys` schema and test block property collector, then parses test SST input.
- `open` command creates a reader over the in-memory object.
- `layout` command calls `Layout().Describe(true, ...)`.
- `props` command reads and prints the properties block.

## Control Flow
The test holds metadata, memory object, and reader across commands so a datadriven script can build, open, inspect layout, and inspect properties in sequence. Existing readers are closed before reopening.

## State and Persistence Behavior
SSTables are built in memory using `objstorage.MemObj`, allowing the test to inspect exact persisted layout without filesystem effects. Writer options may be overridden by datadriven arguments through shared helpers.

## Dependencies and Integration Points
Uses `runBuildMemObjCmd`, `optsFromArgs`, `NewReader`, `colblk.DefaultKeySchema`, test block property collectors, and `Layout.Describe`.

## Risks and Edge Cases
The default table format is pinned to v5 unless overridden, so later format-specific behavior needs explicit datadriven args. Exact layout output is sensitive to encoding and property changes.

## Test Signals
Good signal for columnar writer end-to-end layout, metadata, block properties, and properties serialization.
