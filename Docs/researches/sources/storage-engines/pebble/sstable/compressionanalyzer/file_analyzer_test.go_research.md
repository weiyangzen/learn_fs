# sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer_test.go

## Purpose
Datadriven tests for SSTable-level compression analysis over fixture files.

## Important APIs, Types, and Functions
- `TestFileAnalyzer` supports the `sst` command with one file path per input line.
- The test constructs `NewFileAnalyzer(nil, sstable.ReaderOptions{})`.
- It replaces the test-compressibility compressor with Snappy for platform-stable classification.

## Control Flow
For each input path, the test opens the file from the default VFS, wraps it as an `objstorage.Readable`, and calls `SSTable`. After all files are analyzed, it clears timing metrics and all non-Snappy compression-ratio metrics before formatting `Buckets.String(1)`.

## State and Persistence Behavior
The analyzer accumulates results across all listed SSTables in a single test command. Unstable metrics are zeroed to keep golden output deterministic.

## Dependencies and Integration Points
Uses fixture data under `testdata/file_analyzer`, `compression.GetCompressor`, `metricsutil.WeightedWelford`, `objstorage`, `sstable`, and VFS.

## Risks and Edge Cases
The test intentionally does not assert timing behavior. Platform-dependent MinLZ output is avoided by swapping in Snappy for classification.

## Test Signals
Good integration signal that `FileAnalyzer` can open SSTables, enumerate layout blocks, and produce stable bucket reports.
