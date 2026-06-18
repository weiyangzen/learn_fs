# sources/storage-engines/pebble/replay/workload_capture_test.go

## Purpose
This file validates `WorkloadCollector` behavior against datadriven capture scenarios over an in-memory VFS.

## Important APIs, Types, and Functions
`TestWorkloadCollector` supports commands for `start`, `stop`, `wait`, `create-manifest`, `flush`, `ingest`, `clean`, `cmp-files`, `stat`, and `ls`.

Helpers include `randData`, `writeFile`, and `readFile` for deterministic-size random file creation and verification.

## Control Flow
The test attaches a collector to Pebble options, manually simulates manifest creation, flushes, ingests, and cleaner calls, then waits on the collector's `copyCond` until `filesEnqueued == filesCopied`. Flush and ingest commands create table files and append fake manifest bytes to model version edits.

## State and Persistence Behavior
All source and destination files live in a memory filesystem under `src` and `dst`. The test explicitly keeps the current manifest file open, matching Pebble's active manifest append behavior. Copied-file counts and queued-file counts are internal collector state used for synchronization.

## Dependencies and Integration Points
The test uses Pebble event payload types (`FlushInfo`, `TableIngestInfo`, `ManifestCreateInfo`), base filename parsing, VFS helpers, datadriven testdata, and the collector's wrapped cleaner.

## Risks
The random contents mean equality checks compare bytes but expected outputs focus on sizes and names. The test manually invokes event handlers, so it does not fully exercise Pebble's real event ordering. It does exercise race-prone synchronization with the copy goroutine.

## Test Signals
Strong signals include equality between captured and source files, destination listings after `wait`, deferred cleaner behavior, manifest size growth after flush/ingest, and clean handling for files that are copied or not relevant.
