# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeySelector.java

## Purpose
`KeySelector` models FoundationDB order-based key selection: a base key, an `orEqual` flag, and an offset used by `getKey` and range boundaries.

## Important APIs, Types, And Functions
Factory methods create common selectors: `lastLessThan`, `lastLessOrEqual`, `firstGreaterThan`, and `firstGreaterOrEqual`. `add(int)` returns an offset-adjusted selector. `getKey()` returns a defensive copy; `orEqual`, `getOffset`, and `toString` expose selector fields.

## Control Flow
Transactions pass selectors to JNI by copying the key and reading flag/offset. Range iterators update selectors after each chunk using `firstGreaterThan(lastKey)` or `firstGreaterOrEqual(lastKey)` depending on direction.

## State And Persistence Behavior
The selector is intended immutable; the stored constructor key is not defensively copied, but `getKey` returns a copy. No persistence occurs.

## Dependencies And Integration Points
It is used by `ReadTransaction.getKey`, all range overloads, `RangeQuery`, `MappedRangeQuery`, and debug formatting through `ByteArrayUtil`.

## Risks And Edge Cases
Constructor callers can mutate the passed key array after construction. Large offsets are documented as inefficient. Misunderstanding selector semantics can create off-by-one range boundaries.

## Test Signals
Tests should cover all factory encodings, `add`, key defensive copy on getter, constructor-array mutation behavior, string formatting, and range continuation selectors.
