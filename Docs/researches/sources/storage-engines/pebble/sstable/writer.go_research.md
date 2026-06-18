# sources/storage-engines/pebble/sstable/writer.go

## Purpose
Defines the public SSTable writer facade, raw writer selection, range-key fragmentation, writer metadata, raw writer interface, and a testing logging wrapper.

## Important APIs, Types, And Functions
`NewRawWriter`, `NewRawWriterWithCPUMeasurer`, `Writer`, `NewWriter`, `Set`, `Delete`, `DeleteRange`, `Merge`, `RangeKeySet`, `RangeKeyUnset`, `RangeKeyDelete`, `Close`, `Metadata`, `RawWriter`, `WriterMetadata`, metadata setter methods, and `LoggingRawWriter` are the main exports.

## Control Flow
Raw writer creation chooses row writer for formats through Pebble v4 and columnar writer for newer formats. `NewWriter` configures a keyspan fragmenter for range keys. Point methods validate accumulated errors and strict-obsolete mode before delegating to the raw writer. Range-key methods copy caller bytes into an internal buffer, add spans to the fragmenter, and emit sorted fragmented spans through `encodeFragmentedRangeKeySpan`. `Close` finishes the fragmenter before closing the raw writer.

## State And Persistence Behavior
The writer persists point keys, range deletions, range keys, filters, indexes, and metadata through the selected raw writer. It keeps transient range-key buffers, fragmenter state, accumulated errors, and metadata until close.

## Dependencies And Integration Points
Integrates with object storage writables, row/column raw writers, keyspan fragmentation, blob handles, block handles, table format selection, CPU measurement, and higher-level ingestion/external SST construction.

## Risks And Edge Cases
Strict-obsolete writers reject public point helpers and require lower-level force-obsolete calls. Range key spans must be added in start-key order and have start < end. Returned internal buffers retain copied range-key bytes for writer lifetime. Metadata largest keys are not final until close.

## Test Signals
Covered by writer round-trip tests, range-key datadriven tests, fixture output tests, and lower-level raw writer tests.
