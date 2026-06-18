# sources/storage-engines/leveldb/util/coding_test.cc

## Purpose
`coding_test.cc` verifies LevelDB's primitive encoding contract.

## Important APIs, Types, and Functions
Tests cover `PutFixed32/64`, `DecodeFixed32/64`, varint put/get pointer APIs, `VarintLength`, overflow/truncation handling, and length-prefixed slices.

## Control Flow
The tests generate large ranges and boundary values, encode them, decode sequentially, compare lengths, and check malformed byte sequences return failure.

## State, Dependencies, and Integration
State is local strings and vectors. These tests protect table, log, manifest, and internal key compatibility because those formats reuse the same helpers.

## Risks and Test Signals
Boundary values near powers of two and max integer values are explicitly covered. Fixed decoders' lack of bounds checks is not tested because that is a caller contract.
