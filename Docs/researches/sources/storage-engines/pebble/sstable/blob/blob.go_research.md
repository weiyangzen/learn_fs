# sources/storage-engines/pebble/sstable/blob/blob.go

## Purpose
This file implements blob file writing, footer encoding/decoding, blob file reading, layout inspection, and V2 properties. Blob files store separated values referenced by SSTables.

## Important APIs, Types, and Functions
`FileFormat` defines `FileFormatV1`, `FileFormatV2`, and string formatting. V2 adds property and reserved metaindex handles to the footer.

`FileWriterOptions` controls format, compression, checksum, flush governor, compression counters, and CPU measurement.

`FileWriterStats` reports block count, value count, uncompressed bytes, file length, properties, and likely MVCC garbage bytes.

`FileWriter` writes value blocks asynchronously through a write queue, tracks an `indexBlockEncoder`, and emits metadata/footer on close.

`NewFileWriter`, `AddValue`, `FlushForTesting`, `EstimatedSize`, `Close`, and `writeMetadataBlock` are the primary writer APIs.

`fileFooter` encodes and decodes checksummed V1/V2 footers with magic strings, index handle, checksum type, format, original file number, and V2 properties handle.

`FileReader` wraps a block reader and footer. `NewFileReader`, `ReadValueBlock`, `ReadIndexBlock`, `IndexHandle`, `Layout`, `ReadProperties`, and `FormatVersion` provide read access.

`FileProperties` currently stores compression stats and encodes/decodes them through a key-value colblk block.

## Control Flow
Writer creation initializes encoders, compression, and a goroutine draining compressed value blocks. `AddValue` flushes if the governor says the current block should close, encodes the value, updates stats, and returns a handle with file, block, value ID, and value length. `flush` compresses a value block, updates offsets/stats, and sends it to the write goroutine, which writes bytes and records index block handles. `Close` flushes pending values, waits for the write queue, writes the index block, optionally writes V2 properties, writes the footer, finishes the writable, resets pooled state, and returns stats.

Reader creation reads the max footer length from the tail, decodes the footer, and initializes a block reader with the file checksum type. Value/index/properties reads use block reader APIs and metadata initializers.

## State and Persistence Behavior
The persisted blob file layout is value blocks, index block, optional V2 properties block, and footer. Footer CRC protects footer fields. Index blocks map block IDs to offsets and optional virtual mappings for rewrites. Writer state is pooled and reset after successful close; failed close aborts the writable and keeps the error for subsequent close attempts.

## Dependencies and Integration Points
This code integrates with objstorage `Writable`/`Readable`, sstable `block` compression/checksum/cache APIs, colblk key-value blocks, CRC, CPU measurement, compression counters, file cache options, and blob index/value block metadata.

## Risks
`Close` panics if no blocks were written or block counts mismatch. Async write queue errors are deferred to close. Pooled writer reuse requires thorough reset. Footer magic and format checks must stay backward compatible. `Layout` is diagnostic and reads all physical blocks, so it is not for hot paths.

## Test Signals
`blob_test.go` datadriven writer tests cover V1/V2 output, sparse virtual mappings, file stats, compression counters, reader footer/properties inspection, and handle round-trip via `handle.go`.
