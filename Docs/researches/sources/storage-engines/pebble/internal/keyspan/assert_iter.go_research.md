# sources/storage-engines/pebble/internal/keyspan/assert_iter.go

## Purpose
`assert_iter.go` wraps `keyspan.FragmentIterator` implementations with sanity checks for seek/movement ordering and optional user-key/internal-key bounds.

## Important APIs, Types, And Functions
`Assert` wraps with an `assertIter`. `MaybeAssert` randomly composes invalidating and assert wrappers in invariant builds. `AssertUserKeyBounds` and `AssertBounds` enforce span/key bounds. `assertIter` stores the wrapped iterator, comparer, optional bounds, and last span start/end. It implements all `FragmentIterator` methods and `WrapChildren`.

## Control Flow
Each positioning method delegates, validates the returned span relative to the operation, calls `check`, and returns. `check` validates lower/upper bounds, including trailer ordering for spans starting exactly at the lower internal key, and records span start/end for subsequent `Next`/`Prev` ordering checks.

## State And Persistence Behavior
Wrapper state is in-memory last-span metadata and bounds. It does not alter returned spans. Panics signal invariant failures.

## Dependencies And Integration Points
It depends on `base`, `invariants`, `treesteps`, `context`, `errors`, and formatting. It is used around keyspan iterators in tests and invariant builds.

## Risks And Edge Cases
Bounds are asymmetric because span ends are exclusive user keys while lower can be an internal key. `MaybeAssert` randomness means invariant coverage is probabilistic. Incorrect comparer use would produce false positives or negatives.

## Test Signals
`assert_iter_test.go` validates bound enforcement. Broader iterator tests indirectly exercise seek and ordering assertions.
