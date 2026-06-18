# sources/storage-engines/badger/structs.go

## Purpose
This file defines core Badger storage structs shared by transaction, value-log, and table-writing code: value pointers, value-log entry headers, and user-facing `Entry` values.

## Important APIs, Types, and Functions
- `valuePointer` identifies value-log location by file ID, length, and offset.
- `valuePointer.Less`, `IsZero`, `Encode`, and `Decode` support ordering, sentinel checks, and compact unsafe byte representation.
- `header` stores value-log entry metadata: key length, value length, expiration, internal meta, and user meta.
- `header.Encode`, `Decode`, and `DecodeFrom` serialize/deserialize the value-log header with varints.
- `Entry` is the user-facing mutation object used by transactions and stream writer.
- `NewEntry`, `WithMeta`, `WithDiscard`, `WithTTL`, and `withMergeBit` configure entries.
- `estimateSizeAndSetThreshold` and `skipVlogAndSetThreshold` decide whether values are inline or value-log pointers.

## Control Flow and State Behavior
`valuePointer.Encode` allocates a fixed-size byte slice and writes the struct into it. `Decode` copies bytes into the receiver rather than assigning through an unsafe pointer, avoiding alignment issues. `header.Encode` writes fixed meta bytes followed by unsigned varints for key/value lengths and expiration. `DecodeFrom` reads from a `hashReader` while tracking bytes read, allowing value-log parsing to include checksum accounting.

`Entry` carries mutable internal fields such as commit version, value-log offset, header length, and threshold cache. Size estimation stores the threshold the first time it is used, then estimates either key+value+metas for inline values or key+pointer+metas for value-log values.

## Dependencies and Integration Points
`Entry` is consumed by `Txn.modify`, write batching, value-log writes, and `StreamWriter`. `valuePointer` is encoded into `ValueStruct.Value` with the `bitValuePointer` meta bit and decoded by readers that need to fetch value-log data. `header` is the on-disk value-log record prefix.

## Risks and Edge Cases
Unsafe encoding ties `valuePointer` layout to architecture assumptions; the file mitigates decode alignment issues but still relies on fixed struct size. Header max size must track the field set and varint limits. `WithMeta` sets `UserMeta`, not internal `meta`, which is intentional public API behavior but easy to misread. Threshold caching means callers should not expect changing DB thresholds to alter a reused entry's estimate.

## Test Signals
`structs_test.go` checks that maximum-width header fields encode without panic and that `header` still has five fields, guarding `maxHeaderSize` assumptions.
