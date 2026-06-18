# Research: sources/storage-engines/pebble/tool/wal.go

## Purpose
`tool/wal.go` implements WAL introspection commands. It can dump individual WAL files or merge segmented WAL files into logical logs before decoding Pebble batch records.

## Important APIs, Types, And Functions
`walT` owns the Cobra root plus `dump` and `dump-merged` commands, shared Pebble options, key/value formatters, comparer registry, default comparer, and verbosity flag. `newWAL` initializes default quoted key formatting and size value formatting.

`runDump` reads physical WAL files with `record.NewReader`, parses batches with `pebble.Batch.SetRepr`, and calls `dumpBatch`. `runDumpMerged` accumulates segment files through `wal.FileAccumulator`, then calls `runDumpMergedOne` per logical log. `dumpBatch` decodes `batchrepr.Reader` entries and renders each supported internal key kind.

## Control Flow
For physical dumps, each argument's basename is parsed with `wal.ParseLogFilename` to recover the disk file number used by record checksums. The command loops record-by-record, copies record bytes into a buffer, handles EOF/zeroed/invalid chunks specially, decodes a batch, prints offset, sequence number, count, and length, then prints each batch operation. Merged dumps first group segments into logical logs and use logical offsets from the WAL package.

## State And Persistence
The commands are read-only. Transient state includes a reusable `pebble.Batch`, bytes buffer, accumulated error lists, opened WAL files, and logical log readers. No decoded state is persisted.

## Dependencies And Integration Points
The implementation depends on Pebble batch representation, internal key kinds, range-key decoding, record readers, WAL segment accumulation, Cobra, registered comparers, and shared tool formatters. It is an important debugging bridge between on-disk WAL bytes and human-readable Pebble operations.

## Risks And Edge Cases
Zeroed and invalid chunks are treated like EOF because preallocation and recycling commonly leave such bytes. Sync or corruption errors are printed and accumulated but the command keeps scanning other files. `dumpBatch` handles many key kinds including ingest-with-blobs and range keys; unknown kinds are reported as errors with sequence context. Blob ID varint parsing in ingest-with-blobs stops if malformed, so output may be partial.

## Test Signals
Datadriven `wal_*` tests should cover physical and merged dumps, recycled/preallocated EOF behavior, batch header validation, all major key kinds, range-key decode errors, delete-sized values, ingest SST and ingest-with-blobs formatting, and custom key/value formatters.
