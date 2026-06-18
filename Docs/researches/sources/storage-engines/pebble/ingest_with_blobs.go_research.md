<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/ingest_with_blobs.go -->
# sources/storage-engines/pebble/ingest_with_blobs.go

## Purpose
This file defines the public local-ingest shape for SSTables that have associated blob files, and helper logic for opening those blob files as object-storage readables during ingestion.

## Important APIs, Types, And Functions
`LocalSSTables` is a slice of `LocalSST`; `TotalFiles` counts both SSTs and blob paths. `LocalSST` carries `Path` and `BlobPaths`. `closeReadables` combines close errors. `createBlobReadables` opens blob paths through `Options.FS` and wraps them with `objstorage.NewSimpleReadable`.

## Control Flow
For each blob path, `createBlobReadables` opens the file, builds an `objstorage.Readable`, appends it, and on any open/wrap error closes everything opened so far and combines errors.

## State And Persistence Behavior
The file does not persist metadata itself. It transfers local paths into readable handles for later ingest machinery, preserving ownership boundaries by closing partially initialized resources on failure.

## Dependencies And Integration Points
It depends on `Options.FS`, `objstorage.Readable`, and Cockroach errors. It is consumed by blob-aware ingest paths tested in `ingest_test.go`.

## Risks And Edge Cases
The main risk is resource leakage during partial failure. The code deliberately closes prior readables and combines errors, but callers must still close the returned readables after successful use.

## Test Signals
Blob ingest tests in `ingest_test.go` cover local blob ingestion, flushable blob ingests, WAL recovery, and cleanup of blob files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/ingest_with_blobs.go -->
