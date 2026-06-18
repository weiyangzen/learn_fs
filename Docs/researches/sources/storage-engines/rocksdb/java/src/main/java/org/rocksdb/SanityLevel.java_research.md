# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SanityLevel.java

## Purpose
`SanityLevel` is an enum for compatibility or validation strictness. It maps Java enum constants to byte values expected by native RocksDB APIs.

## Important APIs and Types
- Values: `NONE(0x0)`, `LOOSELY_COMPATIBLE(0x1)`, `EXACT_MATCH(0xFF)`.
- Package-private `getValue()` returns the native byte.
- Package-private `fromValue(byte)` decodes native bytes.

## Control Flow
`fromValue` scans all enum values and returns the first byte match. Unknown bytes throw `IllegalArgumentException` with the numeric byte value in the message.

## State and Persistence Behavior
Enum instances are static and immutable. The byte values may be persisted indirectly if passed into native options or metadata compatibility checks, but this class stores no external state.

## Dependencies and Integration Points
It has no external dependencies beyond Java enum mechanics. It integrates with option or import/export APIs that need sanity-level conversion between Java and native code.

## Risks
`0xFF` is stored in a signed Java byte as `-1`; comparisons remain correct, but diagnostics may print a signed value. Adding native sanity levels requires updating both enum constants and `fromValue` expectations.

## Test Signals
Tests should verify all byte mappings, exact decoding of `0xFF`, and exception behavior for unknown bytes.
