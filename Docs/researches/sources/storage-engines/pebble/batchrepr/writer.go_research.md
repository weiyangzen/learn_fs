# sources/storage-engines/pebble/batchrepr/writer.go

## Purpose
`writer.go` contains the minimal low-level mutation helpers for the batch representation header. It is intentionally small because higher-level record construction lives in `pebble.Batch`.

## Important APIs, Types, And Functions
`SetSeqNum(repr []byte, seqNum base.SeqNum)` writes the first 8 header bytes as a little-endian sequence number. `SetCount(repr []byte, count uint32)` writes bytes 8 through 11 as a little-endian count.

## Control Flow
Both functions perform direct little-endian stores into the supplied slice. There is no validation branch; slices shorter than `HeaderLen` panic by design, matching performance-sensitive internal callers that already own initialized representations.

## State And Persistence Behavior
These helpers mutate the WAL batch header in-place. `Batch.Repr` uses `SetCount` to synchronize the stored count before exposing bytes, and commit paths use sequence-number mutation to publish the assigned sequence number.

## Dependencies And Integration Points
The file depends on `encoding/binary` and `internal/base`. It shares the private `countOffset` and `HeaderLen` constants from `reader.go`.

## Risks And Edge Cases
Main risks are passing a too-short representation or accidentally mutating a representation still observed by another component. The functions do not copy or guard against races; callers must enforce ownership and length.

## Test Signals
`writer_test.go` verifies mutations through datadriven inputs and reuses the reader to inspect header values and pretty-print records.
