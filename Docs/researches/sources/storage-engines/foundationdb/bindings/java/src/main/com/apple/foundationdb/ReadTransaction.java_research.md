# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransaction.java

## Purpose
`ReadTransaction` is the public read-only transaction interface. It defines snapshot semantics, read version control, point reads, key selector resolution, range read overloads, mapped range reads, estimated range sizes, split points, and read conflict helpers.

## Important APIs, Types, And Functions
Key APIs include `isSnapshot`, `snapshot`, `getReadVersion`, `setReadVersion`, `get`, `getKey`, many `getRange` overloads over `KeySelector`, `byte[]`, and `Range`, `getMappedRange`, `getEstimatedRangeSizeBytes`, `getRangeSplitPoints`, `addReadConflictRangeIfNotSnapshot`, and `addReadConflictKeyIfNotSnapshot`. `ROW_LIMIT_UNLIMITED` is `0`.

## Control Flow
Implementations normalize overloads to selector-based forms and return lazy `AsyncIterable`s. Snapshot views route reads with relaxed conflict behavior and suppress conflict range additions.

## State And Persistence Behavior
The interface stores no state. Implementations read from the associated transaction and may add native read conflict ranges unless using snapshot mode.

## Dependencies And Integration Points
It depends on `AsyncIterable`, `AsyncIterator`, `KeySelector`, `Range`, `KeyValue`, `MappedKeyValue`, `StreamingMode`, and `ReadTransactionContext`.

## Risks And Edge Cases
Read-only transactions still need commit for full conflict checking in normal use. Snapshot reads relax isolation. Range iterables depend on transaction lifetime and should be consumed promptly.

## Test Signals
Tests should cover overload normalization, snapshot conflict behavior, range streaming modes, estimated size/split points, mapped range availability, and read retry helpers through contexts.
