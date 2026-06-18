# sources/storage-engines/badger/y/iterator.go

## Purpose
This file defines the serialized value payload stored with Badger keys and a minimal iterator interface shared by lower-level components.

## Important APIs, Types, And Functions
`ValueStruct` stores `Meta`, `UserMeta`, `ExpiresAt`, `Value`, and non-serialized `Version`. `EncodedSize`, `Decode`, `Encode`, and `EncodeTo` define the binary layout: meta byte, user meta byte, varint expiry, then raw value bytes. `Iterator` specifies `Next`, `Rewind`, `Seek`, `Key`, `Value`, `Valid`, and `Close`.

## Control Flow
Encoding writes fixed metadata bytes, varint expiry, and value data either into a caller-provided byte slice or a buffer. Decode reads in the same order and treats the remainder as the value. `sizeVarint` computes the size of a uvarint by shifting until zero.

## State And Persistence Behavior
The encoded `ValueStruct` format is persisted in Badger tables. `Version` is runtime-only and must be populated separately from timestamped keys.

## Dependencies And Integration Points
It depends on `bytes` and `encoding/binary`. Table builders and iterators use this layout, and tests in `y_test.go` verify size calculations.

## Risks And Edge Cases
`Decode` assumes a valid non-empty slice with enough bytes for metadata and varint. `Encode` assumes the destination length is at least `EncodedSize`. Layout changes would break existing SST compatibility.

## Test Signals
`TestSizeVarintForZero` and `TestEncodedSize` cover size math; broader table tests cover encode/decode integration.
