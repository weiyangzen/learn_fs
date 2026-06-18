# sources/storage-engines/pebble/flushable_test.go

## Purpose
Datadriven sanity coverage for `ingestedFlushable`, verifying that SSTables loaded through the ingest metadata path can be exposed through the `flushable` API for point iteration, range deletion iteration, range key iteration, excise handling, and readiness/range-key introspection.

## Important APIs, Types, And Functions
`TestIngestedSSTFlushableAPI` owns the whole file. The `reset` helper opens a DB over a memory filesystem with newest internal format, debug level checks, high L0 thresholds, and automatic compactions disabled. `loadFileMeta` reuses `ingestLoad`, `setSeqNumInMetadata`, `ingestSortAndVerify`, and `ingestLinkLocal` to build metadata and link SSTables. The test constructs `newIngestedFlushable` and calls `newIter`, `newRangeKeyIter`, `newRangeDelIter`, `readyForFlush`, and `containsRangeKeys`.

## Control Flow
Datadriven commands build SSTables, construct a flushable from named local SST paths plus an optional `excise` range, then print point iterator keys, range key spans, range deletion spans, or boolean API results. The sequence number counter is advanced per ingested file and excise so synthetic tombstones and file keys have realistic ordering. Linked files are fsynced before use to mirror ingest durability ordering.

## State And Persistence Behavior
The test writes temporary local SSTables into `vfs.NewMem`, hard-links/copies them into the DB's object provider, and increments table backing references to satisfy file-cache expectations even though the files are not installed in a version. It synthesizes sequence numbers in metadata rather than rewriting table contents. Excise spans become synthetic in-memory range deletion/range-key delete state inside the flushable.

## Dependencies And Integration Points
The test depends on datadriven testdata `testdata/ingested_flushable_api`, `runBuildCmd`, `LocalSSTables`, ingest metadata loading/linking functions, `manifest.TableMetadata`, `vfs`, DB object provider sync, file cache iterators, and the comparer/range-key stack. It is a focused bridge between the ingest pipeline and the flushable read interface.

## Risks And Edge Cases
The setup reuses production ingest helpers while bypassing actual manifest installation, so table backing refs and directory sync are important to avoid false test failures. Excise sequence numbering must match production conventions. Range key and range deletion iterators may be nil, and the test handles nil iterators explicitly to catch incorrect non-nil typed nil behavior.

## Test Signals
Expected datadriven output for point keys, range deletion spans, range key spans, `readyForFlush`, and `containsRangeKey` is the primary signal. Debug checks and file-cache behavior add secondary signals for metadata validity and linked-file readability.
