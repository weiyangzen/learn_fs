# sources/storage-engines/pebble/internal/rangekey/rangekey.go

## Purpose
This file defines Pebble's physical encoding and decoding for range keys (`RANGEKEYSET`, `RANGEKEYUNSET`, and `RANGEKEYDEL`). It converts between `keyspan.Span` state and on-disk internal key/value tuples.

## Important APIs, Types, and Functions
`Encode` is a convenience wrapper around `Encoder`. `Encoder` stores an emit callback and reusable buffers for encoded values, set suffix/value tuples, and unset suffixes. `Encoder.Encode` groups span keys by sequence number and `flush` emits at most one physical set, unset, and delete key per sequence number. `Decode` decodes one physical internal key/value pair into a `keyspan.Span`. `DecodeIntoSpan` appends decoded logical keys into an existing span while checking span bounds. `SuffixValue` represents a logical suffix/value tuple. Encoding helpers compute and write value lengths for set and unset values. `DecodeEndKey` splits the range end key from the rest of a set/unset value and treats delete values as the end key directly. `IsRangeKey` classifies range-key kinds.

## Control Flow and State
`Encoder.Encode` walks the input keys in trailer-descending order, flushing accumulated sets/unsets/deletes whenever the sequence number changes. Sets encode a varstring end key followed by repeated varstring suffix and varstring value pairs. Unsets encode a varstring end key followed by repeated varstring suffixes. Deletes store the end key as the whole value and must have no trailing payload when decoded. The encoder reuses buffers but emits byte slices valid only until the callback returns. Decoding returns slices that alias the encoded value buffer. No state is persisted except the encoded internal keys in sstables.

## Dependencies and Integration
The file uses `encoding/binary`, `crencoding` for varint length sizing, and Pebble `base`, `invariants`, and `keyspan` packages. It is the on-disk contract consumed by sstable readers/writers, range-key merging, compactions, and user iteration.

## Risks and Edge Cases
`DecodeEndKey` requires set/unset values to contain both an end key and at least one byte of remaining payload; malformed or empty payloads return corruption errors. `decodeVarstring` does not explicitly bounds-check `n+int(l)` before slicing, so malformed length values can panic if caller code fails to guard; current tests focus on valid encodings. `DecodeIntoSpan` only checks start-key mismatch under invariants but always checks end-key mismatch. Encoder input is expected to be correctly ordered and contain only range-key kinds.

## Test Signals
`rangekey_test.go` round-trips set suffix/value encodings, set values, unset suffix encodings, unset values, and `IsRangeKey`. It does not exhaustively fuzz corrupt encodings or full `Encoder.Encode` grouping.
