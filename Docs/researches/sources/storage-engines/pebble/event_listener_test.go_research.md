# sources/storage-engines/pebble/event_listener_test.go

## Purpose
Validates event listener logging, callback defaulting, listener teeing, redaction, write stall events, low disk space events, and corruption event payload propagation.

## Important APIs, Types, And Functions
`TestEventListener` is a datadriven scenario over open, close, flush, compact, checkpoint, file deletion toggles, ingest, metrics, and SSTable listing. `TestWriteStallEvents`, `redactLogger`, `mockLogger`, `testAllCallbacksSetInEventListener`, `TestLowDiskReporter`, `mockDiskUsageFS`, `TestSSTCorruptionEvent`, and `TestBlobCorruptionEvent` cover narrower event behavior.

## Control Flow
The datadriven test wraps a memory FS with logging and uses `MakeLoggingEventListener`, overriding timing-sensitive fields for deterministic output. Write-stall tests block table creation at strategic points to force memtable or L0 stalls, then wait for stall-end callbacks. Corruption tests create data, remove or mutate SST/blob files, read keys, and compare emitted `DataCorruptionInfo` to the payload extracted from the returned error.

## State And Persistence Behavior
The tests create temporary in-memory DB state, external SSTables, blob files, and low disk usage snapshots. They intentionally alter filesystem contents to verify corruption reporting rather than normal persistence.

## Dependencies And Integration Points
Uses datadriven testdata, `vfs.WithLogging`, in-memory object provider, `sstable.Writer`, event listeners, disk usage APIs, value separation, and error/corruption helpers. It exercises the event API through real DB operations instead of only direct formatting calls.

## Risks And Edge Cases
Determinism is managed by overriding durations, input bytes, and table-stats behavior. Tests guard that all listener constructors set every callback, redaction hides unsafe error contents, low disk notices respect threshold/frequency rules, and corruption details survive wrapping.

## Test Signals
Signals are exact log output, reflected non-nil callbacks, callback invocation counts, expected stall reason strings, stored low disk info, corruption classification, bounds/path correctness, and equality between event payload and extracted error payload.
