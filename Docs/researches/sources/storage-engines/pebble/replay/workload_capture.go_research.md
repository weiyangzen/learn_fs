# sources/storage-engines/pebble/replay/workload_capture.go

## Purpose
This file implements `WorkloadCollector`, a Pebble event-listener and cleaner wrapper that captures the manifest, flushed SSTables, ingested SSTables, and referenced blob files needed to replay a workload later.

## Important APIs, Types, and Functions
`workloadCaptureState` is a bitset with `obsolete`, `readyForProcessing`, and `capturedSuccessfully` flags.

`WorkloadCollector` owns mutex-protected file state, pending copy queues, manifest descriptors, test condition variables, atomic current manifest and enabled flags, source/destination filesystem config, and a copier condition with stop/done state.

`NewWorkloadCollector` initializes buffers, source directory, state map, and condition variables.

`Attach` adds Pebble event hooks for `FlushEnd`, `ManifestCreated`, and `TableIngested`, then replaces `Options.Cleaner` with a deferring wrapper that calls `w.clean`.

`onFlushEnd`, `onTableIngest`, and `onManifestCreated` enqueue files or manifests while running.

`copyFiles` runs as a background goroutine, draining pending SST/blob paths and manifest updates.

`copyManifests` incrementally copies manifest bytes and closes older rotated manifests when no more bytes can be read.

`copySSTablesAndBlobs` copies queued files and then cleans any that were marked obsolete before capture completed.

`Start`, `WaitAndStop`, `Stop`, and `IsRunning` provide lifecycle control.

## Control Flow
After `Attach`, Pebble events update collector queues. `Start` records destination FS/dir, seeds the current manifest if already known, sets enabled with compare-and-swap, and launches `copyFiles`. The copier waits on a condition, snapshots pending work while holding the mutex, drops the mutex for actual I/O, copies manifest deltas first, then table/blob files, updates copied counts, and broadcasts test waiters. `Stop` flips enabled off, signals the copier, and waits for `done`.

Cleaner interception is central: if capture is not running or a file was already captured, deletion proceeds immediately through the original cleaner. Otherwise the file is marked obsolete and actual deletion is deferred until after copying.

## State and Persistence Behavior
The collector persists captured workload files into a destination directory on a destination VFS. It tracks per-file state by Pebble base filename. Manifest copying is incremental because the active manifest can continue to receive version edits. SSTables and blob files are copied as whole immutable files.

## Dependencies and Integration Points
The collector integrates with `pebble.Options`, `pebble.EventListener`, `pebble.Cleaner`, `base.FileType` naming, `vfs.CopyAcrossFS`, and flush/table ingest metadata. It also now observes blob references from flushed tables through `GetBlobReferenceFiles`.

## Risks
This is concurrency-sensitive code. The lock is intentionally released around I/O and reacquired before loop continuation; incorrect lock ordering could deadlock or race. Panics are used for copy/open/close failures in the background goroutine, so production callers should treat collector failures as fatal. `copySSTablesAndBlobs` calls `cleanFile` with `FileTypeTable` even for blob paths, which depends on the wrapped cleaner tolerating or ignoring the type. Manifest seeding and rotation must stay aligned with Pebble manifest lifecycle or replay can miss edits.

## Test Signals
The paired datadriven collector test exercises start/stop, manifest creation, flush, ingest, deferred cleaning, file comparison, waiting for copy completion, and destination listings.
