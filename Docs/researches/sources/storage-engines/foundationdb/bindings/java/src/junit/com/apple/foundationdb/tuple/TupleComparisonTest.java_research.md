# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleComparisonTest.java

## Purpose
`TupleComparisonTest` verifies that semantic tuple comparison agrees with packed-byte unsigned comparison across a broad set of tuple element types and edge cases.

## Important APIs, Types, and Functions
It builds a static ordered list of `Tuple` instances containing integers, `BigInteger`s, signed zeros, infinities, NaNs, byte arrays, nested tuples, Unicode strings, UUIDs, booleans, lists, and complete `Versionstamp`s. A cartesian provider feeds every ordered pair into `testCanCompare`.

## Control Flow
For each tuple pair, the test copies tuples from items, computes semantic `compareTo`, compares packed bytes with `ByteArrayUtil.compareUnsigned`, and compares the original tuple's `compareTo`. It asserts the sign of all comparison methods matches.

## State and Persistence Behavior
The comparison corpus is static immutable test data. There is no external state.

## Dependencies and Integration Points
This test is central to tuple encoding compatibility: FoundationDB tuple keys must preserve logical ordering when packed into byte strings used by the database.

## Risks and Edge Cases
The cartesian product is large and can be slow. It verifies sign agreement but not exact comparator magnitude. The expected order is implicit in the corpus and `Tuple.compareTo`, so a shared bug in semantic and implicit tuple comparison would only be caught by byte comparison.

## Test Signals
Passing indicates packed tuple bytes preserve semantic ordering across numeric, string, binary, nested, UUID, boolean, and versionstamp values.
