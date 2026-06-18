# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MutableOptionValue.java research

## Purpose

`MutableOptionValue` is the typed value wrapper used by mutable-option builders. It centralizes conversion between Java objects and the string forms sent to RocksDB's mutable-option APIs.

## Important APIs and types

Static factories create wrappers for strings, doubles, longs, ints, booleans, int arrays, and enums. Abstract conversion methods include `asDouble`, `asLong`, `asInt`, `asBoolean`, `asIntArray`, `asString`, and `asObject`. Nested classes implement type-specific conversions and serialization; int arrays are joined with `AbstractMutableOptions.INT_ARRAY_INT_SEPARATOR`, and enum values serialize as `name()`.

## Control flow

Builders create or parse `MutableOptionValue` instances, then request the conversion required by a `MutableOptionKey.ValueType`. Unsupported conversions throw `NumberFormatException` or `IllegalStateException`. Numeric conversions can downcast with range checks for int.

## State and persistence behavior

Each wrapper stores an immutable reference or primitive value, except int arrays are stored by reference. The values become serialized strings in mutable-option payloads; persistence effects depend on the option being applied.

## Dependencies and integration points

It depends on `AbstractMutableOptions.INT_ARRAY_INT_SEPARATOR` and is used by `AbstractMutableOptionsBuilder`, `MutableDBOptions`, and `MutableColumnFamilyOptions`.

## Risks and test signals

Risks include array mutability after wrapping, `Boolean.parseBoolean` treating unknown strings as false, numeric truncation from double/long to int arrays, and inconsistent exception types. Tests should cover all valid and invalid conversions, enum serialization, int-array separator handling, and defensive behavior around mutable arrays.
