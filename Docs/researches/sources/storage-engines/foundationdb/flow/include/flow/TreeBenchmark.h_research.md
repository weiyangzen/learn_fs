# sources/storage-engines/foundationdb/flow/include/flow/TreeBenchmark.h

## Purpose
Benchmark harness for ordered tree-like containers. It generates deterministic random keys, times insert/find/bounds/scan/erase phases, and asserts basic ordering and emptiness invariants.

## Important APIs, Types, And Functions
`opTimer` prints Kops/sec on destruction. `timedRun` applies a callable across a range under an `opTimer`. `MapHarness<K>` adapts `std::map<K, int>` to the expected tree API. `treeBenchmark(T&, F)` drives the full benchmark. `randomStr(Arena&)` and `randomInt()` provide deterministic key generators.

## Control Flow
`treeBenchmark` creates one million keys, inserts them, validates finds and lower bounds, executes upper bounds, sorts/uniques keys, verifies sequential scan order, shuffles, erases all keys, and asserts the tree is empty.

## State And Persistence Behavior
All state is in-memory benchmark data. There is no persistence. Deterministic RNG makes results repeatable for a given simulation seed.

## Dependencies And Integration Points
Depends on `flow/flow.h` for `timer`, `ASSERT`, `Arena`, `StringRef`, and `deterministicRandom`. Target trees must expose `key_type` and map-like iterator/search operations. Useful for storage/tree performance tests.

## Risks And Edge Cases
Duplicates are removed only after initial lookup phases, so target containers must tolerate duplicate inserts consistently. `upper_bound` is timed but not checked. Scan assumes at least one key and strict sorted iteration.

## Test Signals
Successful assertions in find, lower-bound, scan, sorted find, erase, and final empty checks are the primary correctness signals; throughput lines provide performance signals.
