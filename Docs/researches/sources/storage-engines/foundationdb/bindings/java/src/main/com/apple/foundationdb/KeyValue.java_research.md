# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyValue.java

## Purpose
`KeyValue` is the public value type representing one key/value pair returned from range reads and nested mapped-range results.

## Important APIs, Types, And Functions
The constructor stores `key` and `value`; `getKey` and `getValue` return those arrays. `equals`, `hashCode`, and `toString` use array-content comparison and printable byte formatting.

## Control Flow
Range result constructors and direct-buffer iterators instantiate `KeyValue` for each row; clients consume instances through `AsyncIterator` or `asList`.

## State And Persistence Behavior
The object stores references to byte arrays and does not defensively copy them. It is otherwise immutable by field assignment, but array contents remain mutable.

## Dependencies And Integration Points
It is central to `RangeResult`, `RangeQuery`, `MappedKeyValue`, `LocalityUtil`, and `ReadTransaction` range APIs.

## Risks And Edge Cases
Callers can mutate arrays returned by getters, changing equality/hash behavior after insertion into hash collections. Large values in `toString` may be expensive or verbose.

## Test Signals
Tests should cover content equality, hash consistency, string formatting for binary keys, and mutation implications if arrays are changed after construction.
