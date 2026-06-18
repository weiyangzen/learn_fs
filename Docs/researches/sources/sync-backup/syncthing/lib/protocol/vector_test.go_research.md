# sources/sync-backup/syncthing/lib/protocol/vector_test.go

## Purpose
Unit tests for vector-clock update, merge, copy, counter lookup, and comparison semantics.

## Important APIs, Types, and Functions
`TestUpdate`, `TestCopy`, `TestMerge`, `TestCounterValue`, and `TestCompare` exercise `Vector.updateWithNow`, `Update`, `Copy`, `Merge`, `Counter`, `Compare`, and convenience predicates.

## Control Flow
The tests build explicit vectors with sorted counters, call vector operations, and compare expected orderings. `TestCompare` uses a large table covering empty vectors, missing zero counters, equal values, greater/lesser relationships, concurrent relationships, and `math.MaxUint64` values.

## State and Persistence Behavior
All state is local test data. `TestCopy` specifically checks that copy results do not share backing storage with the original.

## Dependencies and Integration Points
Depends on `math` and `testing`. It is directly tied to file version conflict behavior in higher-level Syncthing code because vector comparisons decide whether a file version is ancestor, descendant, equal, or concurrent.

## Risks and Edge Cases
The tests assume sorted vector inputs, matching production expectations. They do not cover malformed unsorted vectors or string/wire round trips in this file. Time-dependent public `Update` is avoided by using `updateWithNow` for deterministic assertions.

## Test Signals
Passing tests indicate stable vector ordering, merge behavior, and convenience predicate results across common and boundary cases.
