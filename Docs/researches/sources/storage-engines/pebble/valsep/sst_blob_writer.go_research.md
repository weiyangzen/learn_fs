# Research: sources/storage-engines/pebble/valsep/sst_blob_writer.go

## Purpose
`valsep/sst_blob_writer.go` provides `SSTBlobWriter`, a wrapper that writes an SSTable plus zero or more blob value files for later ingestion. It applies value-separation policy while exposing a writer interface close to `sstable.Writer`.

## Important APIs, Types, And Functions
`SSTBlobWriter` holds the public `SSTWriter`, chosen `ValueSeparation` strategy, accumulated error, blob file-number counter, close state, strict-obsolete flag, scratch KV, and metadata for blob files written. `SSTBlobWriterOptions` configures SST and blob writer options, whether blob files are disabled, minimum separation sizes, span policy, and `NewBlobFileFn`.

`NewSSTBlobWriter` builds the SST writer, applies fast-compression span policy, chooses `NeverSeparateValues` or `NewWriteNewBlobFiles`, and supplies a blob-object factory that assigns unique synthetic disk file numbers. `Set` adds an ordinary SET key with sequence zero. `BlobWriterMetas` returns blob stats after close. `Close` closes both SST and value-separation outputs. `HandleTestKVs` maps parsed datadriven KVs/spans into writer calls.

## Control Flow
Construction computes the active minimum separation size, honoring span-policy overrides and disable flags. `Set` first checks accumulated errors and strict-obsolete mode, prepares an internal SET KV, asks the raw SST writer whether the value is likely MVCC garbage, and delegates to the selected `ValueSeparation.Add`. `Close` closes the SST first, finishes value separation, collects new blob file stats, marks the writer closed, and returns combined errors.

## State And Persistence
The writer persists an SST object and any created blob objects through `objstorage.Writable`. It tracks blob metadata in memory until close. The `ValueSeparator` writes inline blob handles into the SST and writes separated values into blob files.

## Dependencies And Integration Points
It integrates `sstable.Writer`, `sstable.RawWriter`, `blob.FileWriter`, span policies, value-storage policy adjustments, short attributes, object storage, and ingest metadata. It is the external writer-side bridge between Pebble tables and blob value files.

## Risks And Edge Cases
`BlobWriterMetas` is invalid before close. Strict obsolete mode forbids `Set` and requires raw writer paths. A missing `NewBlobFileFn` would fail when the first value is separated. The synthetic file number starts at zero and is only used to produce reference indexes, so consumers must not treat it as final manifest identity without translation. Accumulated invalid-value callback errors are combined with writer errors.

## Test Signals
Datadriven tests exercise build options, span-policy overrides, disabled separation, MVCC garbage thresholds, output table size, blob file count, and blob stats. `HandleTestKVs` also verifies non-SET operations pass through to the underlying SST writer.
