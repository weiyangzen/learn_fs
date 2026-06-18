# Research: sources/storage-engines/pebble/valsep/sst_blob_writer_test.go

## Purpose
`valsep/sst_blob_writer_test.go` provides datadriven tests for `SSTBlobWriter`. It checks how external SST construction produces table metadata and blob file metadata under different value-separation options.

## Important APIs, Types, And Functions
`TestSSTBlobWriter` calls `runDataDriven` over `testdata/sst_blob_writer`. `parseSpanPolicy` parses a compact span-policy string into `base.SpanPolicy`, supporting `no-value-separation`, `value-separation-min-size`, and `disable-value-separation-by-suffix`. `parseBuildSSTBlobWriterOptions` extracts datadriven command args. `runDataDriven` implements the `build` command.

## Control Flow
For each `build` command, the test creates a logging in-memory FS, opens an object store, configures writer options with `testkeys.Comparer` and table format Pebble v7, supplies a blob-file factory that increments a counter, creates an SST object, parses input KVs/spans, feeds each to `HandleTestKVs`, closes the writer, reads table metadata and blob metadata, and prints a stable summary.

## State And Persistence
All files live in an in-memory VFS/object store. The test persists an SST object and any blob objects only for the duration of the datadriven command. Logging FS output is captured but not directly printed in the current returned output except through errors.

## Dependencies And Integration Points
The test integrates `datadriven`, `objstorageprovider`, `vfs.WithLogging`, `sstable.ParseTestKVsAndSpans`, `testkeys.Comparer`, and `require` assertions. It directly validates the external writer API rather than a DB compaction path.

## Risks And Edge Cases
The span-policy parser is intentionally narrow and fails on unknown options. It assumes one span policy for the whole SST. The test enforces `blobFileCount == len(blobMetas)`, so missing metadata collection after writing blobs is caught. Deferred close avoids leaks if a command exits early.

## Test Signals
Signals include table size changes, zero versus nonzero blob file creation, blob stats string formatting, option parsing failures, minimum-size overrides, suffix-based disablement, and correct handling of parsed point/range operations.
