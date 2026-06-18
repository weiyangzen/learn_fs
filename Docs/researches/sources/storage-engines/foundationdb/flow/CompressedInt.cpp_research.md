# sources/storage-engines/foundationdb/flow/CompressedInt.cpp

## Purpose
`CompressedInt.cpp` provides unit coverage and debug bit-printing utilities for the templated `CompressedInt` serialization type declared in `flow/CompressedInt.h`.

## Important APIs, Types, and Functions
`printBitsLittle` and `printBitsBig` print raw bit patterns for diagnostics. `testCompressedInt<IntType>` serializes a value through `BinaryWriter`, optionally verifies exact encoded bytes, deserializes through `BinaryReader`, and checks the decoded value. `forceLinkCompressedIntTests` forces test linkage.

## Control Flow
The single test case validates known encodings for small signed integers and one large `int64_t`, then generates ten million deterministic bit-pattern values and round-trips them as 64-bit, 32-bit, and 16-bit compressed integers.

## State and Persistence Behavior
There is no persistent state. Serialized byte strings are transient `BinaryWriter` values using the current network protocol version from `g_network`.

## Dependencies and Integration Points
The file depends on Flow unit tests, `CompressedInt.h`, `BinaryReader`, `BinaryWriter`, `AssumeVersion`, and deterministic randomness. It validates a serialization primitive used anywhere compact integer wire/disk encoding is needed.

## Risks and Edge Cases
The randomized loop is intentionally large and can be expensive. Because it casts a growing `int64_t` into smaller integer types, it exercises truncation behavior as seen by template instantiation. Exact expected byte strings lock compatibility for representative encodings.

## Test Signals
Failures print original, encoded, expected, and decoded bit patterns before assertions. The test case name is `/flow/compressed_ints`.
