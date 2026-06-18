# sources/storage-engines/pebble/sstable/compressionanalyzer/file_analyzer.go

## Purpose
Analyzes all relevant blocks in an SSTable file by reading its layout and feeding block data into `BlockAnalyzer`.

## Important APIs, Types, and Functions
- `FileAnalyzer` stores a `BlockAnalyzer`, optional token-bucket read limiter, and SSTable reader options.
- `NewFileAnalyzer`, `Buckets`, `Close`, `SSTable`, and `sstBlock` implement lifecycle and file analysis.

## Control Flow
`SSTable` resets compressors, opens an `sstable.Reader`, gets the layout, builds a list of data/index/filter/range/value/metadata blocks, sorts them by offset for readahead, and calls `sstBlock` for each non-empty handle. `sstBlock` rate-limits by block length when configured, reads the block through the block reader without metadata initialization, analyzes it, and releases the buffer.

## State and Persistence Behavior
The analyzer does not write files. It closes the readable through the reader in normal cases and explicitly closes it if reader creation fails. Accumulated results remain in the embedded `BlockAnalyzer`.

## Dependencies and Integration Points
Depends on `sstable.Reader`, `Layout`, `objstorage`, `block.Reader`, `blockkind`, and `tokenbucket`. It rejects cache-enabled reader options because the analyzer does not populate block metadata for cached entries.

## Risks and Edge Cases
Blob files are not supported. Zero-length handles are skipped, but the block list may include absent optional handles. Cache options panic on construction. The top index is appended even if empty and skipped later.

## Test Signals
Covered by `file_analyzer_test.go`, which analyzes fixture SSTables and normalizes unstable timing/compression outputs.
