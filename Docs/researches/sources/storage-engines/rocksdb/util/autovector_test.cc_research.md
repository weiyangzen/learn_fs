# sources/storage-engines/rocksdb/util/autovector_test.cc

Purpose: verifies functional behavior and provides ad hoc performance comparisons for `autovector`. It focuses on stack versus heap transition, construction APIs, copy semantics, iterator behavior, and relative cost against `std::vector`.

Important tests and helpers: `AssertAutoVectorOnlyInStack` checks whether overflow storage has been allocated. `PushBackAndPopBack` inserts `1000 * kSize` integers, verifies size and indexing, then pops all elements. `EmplaceBack` builds pairs of integer and string values. `Resize` grows from stack-only to overflow and shrinks. `CopyAndAssignment` checks copy construction and assignment for stack and heap-sized vectors using `AssertEqual`. `Iterators` exercises forward, reverse, const, arithmetic, dereference, and arrow operations. `PerfBench` prints creation/insertion and sequence access timings for string and integer vectors.

Control flow and state: tests create fresh containers and validate visible state after each mutation. The benchmark test is still a `TEST_F`, so it runs with normal tests and prints to stdout, but has no assertions on performance.

Dependencies and integration: includes `util/autovector.h`, RocksDB test harness, `Env` timing, and `string_util`. It installs the RocksDB stack trace handler in `main`.

Risks and test signals: coverage is useful for ordinary operations but misses move construction/assignment, self-assignment behavior, non-default-constructible types, exception safety, and destructor-counting lifetime checks. Because `PerfBench` is assertion-light and potentially expensive, it is a smoke/performance diagnostic rather than a correctness gate. The test does validate stack-to-heap transitions and iterator arithmetic across both storage regions.
