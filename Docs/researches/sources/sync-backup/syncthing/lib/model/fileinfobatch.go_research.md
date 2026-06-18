# sources/sync-backup/syncthing/lib/model/fileinfobatch.go

## Purpose
Batches `protocol.FileInfo` slices for database updates or index messages, limiting batch size by serialized bytes and item count.

## Important APIs, Types, and Functions
Constants `MaxBatchSizeBytes` and `MaxBatchSizeFiles` define flush thresholds. `FileInfoBatch` stores pending infos, byte size, flush function, and sticky error. Methods include `NewFileInfoBatch`, `SetFlushFunc`, `Append`, `Full`, `FlushIfFull`, `Flush`, `Reset`, and `Size`.

## Control Flow
`Append` initializes capacity, appends a file, and adds protobuf wire size. `Full` checks both thresholds. `FlushIfFull` delegates to `Flush` only when full. `Flush` no-ops on empty, calls the flush function, stores any error as sticky, and resets on success. After an error, `Append` panics and flush attempts return the same error until `Reset`.

## State and Persistence Behavior
State is in-memory only. Persistence side effects are delegated to the caller-provided flush function, commonly database updates or protocol sends.

## Dependencies and Integration Points
Uses `protocol.FileInfo.ToWire(true)` and `google.golang.org/protobuf/proto.Size`. Used heavily by folder scanning, pulling, send-only override, and receive-only revert code to control database update sizes.

## Risks
Not concurrency-safe. A nil flush function will panic if `Flush` is called with data. Sticky error semantics require callers to reset explicitly before reuse.

## Test Signals
`fileinfobatch_test.go` covers sticky error behavior and reset recovery, but not threshold calculation, protobuf sizing, or nil flush behavior.
