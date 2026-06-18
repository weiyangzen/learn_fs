# sources/storage-engines/foundationdb/flow/IndexedSet.cpp

## Purpose
Holds tests and invariant helpers for the header-only `IndexedSet<>` AVL tree/map implementation.

## Important APIs, Types, And Functions
`ISGetHeight()` and `IndexedSet<T, Metric>::testonly_assertBalanced()` recursively verify BST ordering, parent links, balance values, AVL bounds, and metric totals. String/char comparison overloads support heterogenous map lookups. `IndexedSetHarness` adapts `IndexedSet` to `treeBenchmark()`. `forceLinkIndexedSetTests()` forces test linkage.

## Control Flow
Tests build large indexed sets, run range erases, randomized insert/erase sequences, string map operations, performance benchmark harnesses, integer insert/find/erase/order checks, constructor/destructor accounting, comparison against `std::set::upper_bound`, metric-based `index()`/`sumRange()` checks, full erase, and const-iterator static assertions.

## State And Persistence Behavior
All state is in-memory test data. Metrics are stored in tree nodes by the header implementation and validated here.

## Dependencies And Integration Points
Depends on `flow/IndexedSet.h`, deterministic random, `TreeBenchmark`, `UnitTest`, `fmt`, `Arena`, `Map`, STL sets/vectors/deques/random, and `NoMetric`/metric variants.

## Risks And Edge Cases
Large million-operation tests are expensive but valuable for balancing, destructor, and metric regressions. `testonly_assertBalanced()` assumes every node was inserted with metric `3`, so it is not a generic invariant checker for arbitrary metrics. Performance tests print rates and may be environment-sensitive.

## Test Signals
Registered tests cover range erase, random ops, strings, performance comparisons, integer correctness, destructor matching, std::set comparison, all-number metric indexing/ranges, and const iterator type guarantees.
