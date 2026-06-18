# sources/storage-engines/foundationdb/fdbrpc/bench/BenchSupport.h

## Purpose
`BenchSupport.h` provides a small reusable `InputGenerator<T>` for fdbrpc benchmark files that need deterministic precomputed input values.

## Important APIs, Types, and Functions
`InputGenerator<T>` has a default constructor, a generator constructor taking `n` and a callable, and `next()` returning a const reference to the next precomputed value.

## Control Flow
The constructor reserves `n` values and fills the vector by repeatedly calling the supplied generator. `next()` increments `lastIndex`, wraps to zero at the end, and returns the current element.

## State and Persistence Behavior
State is process-local: a vector of generated values and the last returned index. It does not persist output.

## Dependencies and Integration Points
It depends on `flow/flow.h` for `ASSERT` and is included by `BenchSamples.cpp`.

## Risks and Edge Cases
The default constructor leaves `lastIndex` uninitialized, so callers must not call `next()` before constructing with data. `next()` assumes `data` is non-empty; only the generator constructor asserts `n > 0`.

## Test Signals
Benchmark success in `BenchSamples.cpp` exercises the generator's wrap-around behavior.
