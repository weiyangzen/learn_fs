# sources/storage-engines/foundationdb/fdbrpc/bench/BenchAsyncFileWriteCheckerLRU.cpp

## Purpose
This benchmark measures the update, remove, and truncate workload of `AsyncFileWriteChecker::LRU`, approximating random page tracking for a large file.

## Important APIs, Types, and Functions
The file defines `lru_test(benchmark::State&)` and registers it with `BENCHMARK(lru_test)`. It uses `AsyncFileWriteChecker::LRU`, `AsyncFileWriteChecker::WriteInfo`, deterministic random numbers, and a `std::set<uint32_t>` of existing pages.

## Control Flow
For each benchmark iteration, the test performs 10,000 operations. If the known set is small or a random draw is above 0.5, it updates a random page with a changing timestamp. If the random draw is below 0.45, it removes a random existing page. Otherwise it truncates to a random page in the first half and erases the local set tail.

## State and Persistence Behavior
State is in-memory inside the benchmark process: the LRU object and the local page set. It models a file up to `150000000` pages but does not touch disk.

## Dependencies and Integration Points
It depends on Google Benchmark, `AsyncFileWriteChecker.h`, and Flow deterministic random support. It integrates with the `fdbrpc_bench` target.

## Risks and Edge Cases
The local `exist` set persists across benchmark iterations, so later iterations benchmark a warmed and growing structure. Random `std::advance` over `std::set` is linear and contributes overhead that is not part of the LRU implementation. The comment says 600GB, which assumes 4KB pages.

## Test Signals
The signal is benchmark throughput and aggregate timing, not correctness assertions. Crashes or assertion failures in the LRU implementation are secondary signals.
