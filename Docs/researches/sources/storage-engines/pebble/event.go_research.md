# sources/storage-engines/pebble/event.go

## Purpose
Defines Pebble's event payloads, formatting, default event listener behavior, logging listener, listener teeing, low disk space reporting, and corruption reporting metadata.

## Important APIs, Types, And Functions
Important exported payloads include `DataCorruptionInfo`, `LevelInfo`, `BlobFileCreateInfo`, `BlobFileDeleteInfo`, `BlobFileRewriteInfo`, `BlobFileInfo`, `CompactionInfo`, `FlushInfo`, `DownloadInfo`, manifest/table/WAL events, `TableIngestInfo`, `WriteStallBeginInfo`, `LowDiskSpaceInfo`, and `PossibleAPIMisuseInfo`. `EventListener` contains callback fields for all event types. `EnsureDefaults`, `MakeLoggingEventListener`, `TeeEventListener`, `lowDiskSpaceReporter.Report`, `DB.reportCorruption`, and `ExtractDataCorruptionInfo` are the main behavior.

## Control Flow
Event producers populate an info struct and call the configured listener synchronously. Formatting paths implement `redact.SafeFormatter` so log output is safe by default. `EnsureDefaults` fills nil callbacks, using logger-backed background errors and fatal corruption reporting when possible. `MakeLoggingEventListener` logs every callback. `TeeEventListener` forwards to two listeners after defaulting both. `lowDiskSpaceReporter` emits when disk availability crosses descending thresholds or after a repeat interval.

## State And Persistence Behavior
The file does not mutate durable DB state. It carries event state to users and logs. `reportCorruption` enriches corruption errors with object path, remote locator, user-key bounds, details, and corrupt block data, then joins a hidden carrier error so callers can later extract the payload.

## Dependencies And Integration Points
Integrates with compactions, flushes, blob rewriting, ingestion, downloads, manifests, WALs, table stats, validation, write stalls, disk health checks, low disk monitoring, and corruption detection. It depends on `manifest`, `base`, `objstorage`, `remote`, `vfs`, humanizers, `redact`, and CockroachDB errors.

## Risks And Edge Cases
Callbacks are synchronous and can block DB work if user code is slow. Some callbacks run on hot read or disk-health paths and must not perform blocking I/O. Redaction must distinguish safe local paths from potentially unsafe remote paths. Formatting divides by duration for rates, so callers should provide sensible durations. `PossibleAPIMisuse` includes false-positive caveats for SingleDelete under delete-only compactions.

## Test Signals
Covered by event listener datadriven tests, redaction tests, callback default coverage, low disk reporter tests, block-data hex formatting tests, and corruption event tests for SSTables and blobs.
