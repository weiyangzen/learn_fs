# sources/storage-engines/foundationdb/fdbclient/TupleVersionstamp.cpp

## Purpose
`TupleVersionstamp.cpp` implements the fixed-size tuple versionstamp value used by `Tuple`. A tuple versionstamp contains an 8-byte transaction version, 2-byte batch number, and 2-byte user version in big-endian order.

## Important APIs, types, and functions
Constructors accept either an existing `StringRef` of exactly `VERSIONSTAMP_TUPLE_SIZE` bytes or individual `version`, `batchNumber`, and `userVersion` fields. Accessors include `getVersion()`, `getBatchNumber()`, `getUserVersion()`, `begin()`, `size()`, and equality comparison.

## Control flow
The `StringRef` constructor validates exact size and throws `invalid_versionstamp_size` otherwise. The field constructor allocates a 12-byte string and writes all fields in big-endian form. Accessors read from fixed offsets, convert from big-endian, and return typed values. Equality compares decoded field values rather than raw bytes.

## State and persistence behavior
The object owns a 12-byte `Standalone<StringRef>` value. It does not persist by itself, but `Tuple::append(TupleVersionstamp)` embeds this byte sequence into ordered tuple keys.

## Dependencies and integration points
It depends on `TupleVersionstamp.h`, endian helpers, Flow string ownership, and tuple constants. It integrates directly with `Tuple.cpp` versionstamp append/get behavior and any API that stores versionstamped tuple keys.

## Risks and edge cases
The code uses fixed-offset reinterpret casts, so size validation is essential. Batch and user versions are returned as signed `int16_t` even constructor parameters are `uint16_t`, which can matter for values above `INT16_MAX`. Equality normalizes through decoded values, so it is robust for canonical byte representation but still assumes the 12-byte layout.

## Test signals
Useful tests include constructor size validation, field constructor byte layout, accessor round trips for boundary values, equality comparisons, and integration through `Tuple::append()` and `Tuple::getVersionstamp()`.
