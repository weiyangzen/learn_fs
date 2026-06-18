# sources/storage-engines/pebble/batchrepr/reader.go

## Purpose
`batchrepr/reader.go` provides low-level decoding for Pebble's stable binary batch representation. It is used by `pebble.Batch`, WAL replay, tests, and any code that must scan a serialized batch without owning higher-level batch state.

## Important APIs, Types, And Functions
Exports include `ErrInvalidBatch`, `HeaderLen`, `IsEmpty`, `ReadHeader`, `Header`, `Header.String`, `ReadSeqNum`, `Read`, `Reader`, `Reader.Next`, `DecodeStr`, and `DecodeBlobFileIDs`. `HeaderLen` is fixed at 12 bytes: 8 bytes sequence number and 4 bytes count. `Reader` is a byte-slice cursor over records after the header.

## Control Flow
`ReadHeader` validates the slice length and decodes little-endian header fields. `Read` skips the header or returns nil for empty/short inputs. `Reader.Next` reads a kind byte, rejects kinds above `InternalKeyKindMax`, decodes the user key as a varstring, and conditionally decodes a value varstring for record kinds that carry values. `DecodeStr` has a fast path for short inputs where only one-byte varints can be valid and an unsafe unrolled slow path for up to 5-byte uint32 varints. `DecodeBlobFileIDs` reads a count varint, bounds allocation by remaining bytes, and decodes each blob ID varint.

## State And Persistence Behavior
The reader is stateless except for advancing the `Reader` slice cursor. Returned key/value slices alias the input representation, so callers must preserve the backing bytes. Errors are marked corruption errors via `base.MarkCorruptionError`, preserving DB corruption semantics for bad WAL or externally supplied batch bytes.

## Dependencies And Integration Points
It depends on `encoding/binary`, `unsafe`, `internal/base`, and `github.com/pkg/errors`. `pebble.Batch.refreshMemTableSize`, `Apply`, `newFlushableBatch`, tests, and writer pretty-printing all rely on this decoder to interpret records consistently with the WAL format.

## Risks And Edge Cases
Primary risks are malformed varints, truncated records, invalid kind tags, huge blob counts causing allocation panics, and unsafe reads in the slow path. The code mitigates the unsafe path by using it only when `len(data) > 128`, which guarantees enough bytes for five-byte loads. `ReadSeqNum` deliberately does not validate length and will panic on too-short input; callers must use it only on validated or performance-sensitive paths.

## Test Signals
`reader_test.go` covers datadriven scans, empty detection, `DecodeStr` truncation and fast/slow paths, blob ID malformed inputs, huge count defense, round trips, and truncated `Reader.Next` records.
