# sources/storage-engines/foundationdb/fdbclient/bench/GlobalData.h

Purpose: declarations and small input generator utilities for fdbclient benchmarks.

Important APIs and types: declares `getKV(size_t keySize, size_t valueSize)` and `getKey(size_t keySize)`. Defines `InputGenerator<T>`, which precomputes `n` values from a generator function and cycles through them with `next()`.

State and persistence: `InputGenerator` stores a vector of generated values and a `lastIndex` cursor. It is transient benchmark helper state.

Dependencies and integration: includes `FDBTypes.h` and `flow/flow.h`; paired with `GlobalData.cpp` and usable by any benchmark in the local target.

Risks: `lastIndex` is an `int` while `data.size()` is unsigned; construction asserts `n > 0`, so normal cycling is safe for practical benchmark sizes. `next()` returns a const reference, so callers must not mutate through it or outlive the generator.

Test signals: no direct tests; benchmark compilation and use exercise the declarations.
