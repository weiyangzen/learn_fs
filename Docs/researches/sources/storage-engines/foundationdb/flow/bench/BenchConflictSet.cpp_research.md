## sources/storage-engines/foundationdb/flow/bench/BenchConflictSet.cpp

Purpose: this benchmark compares a simple `std::vector<bool>` conflict set against a word-packed `uint64_t` bitset implementation for FoundationDB-style range conflict detection workloads.

Important types and APIs: `MiniConflictSet` stores one boolean per key and implements `set(begin,end)`, `any(begin,end)`, and `clear()`. `WordBitsetConflictSet` stores 64-bit words and implements the same API with range masks across partial and full words. `ConflictRange` holds begin/end. `getSharedWorkload` creates deterministic static write/query ranges parameterized by number of ranges, keyspace, sparsity, and workload type. Benchmarks cover set/query for both implementations, a correctness verification benchmark, and a realistic combined write/read workload selected by template parameter.

Control flow: workload generation seeds deterministic random state and builds static vectors once per template instantiation. Set benchmarks construct a fresh conflict set each iteration and apply ranges. Query benchmarks prepopulate once, then count conflicts over read ranges inside the timed loop. Realistic benchmarks perform both writes and reads per iteration. Correctness benchmark compares both implementations over shared workloads and calls `SkipWithError` on mismatch.

State and persistence behavior: all state is in-memory benchmark data. Static workload vectors persist for the process lifetime to avoid regeneration inside timed loops. No external persistence.

Dependencies and integration points: depends on Google Benchmark, Flow `IRandom`, `Error`/`ASSERT`, standard vectors/algorithms/cstdint/limits. The benchmark models behavior similar to a conflict set from `SkipList.cpp` and can inform replacement or optimization decisions.

Risks: neither implementation does bounds checks on `begin`/`end` beyond empty ranges; workload generation must keep ranges within keyspace. `WordBitsetConflictSet` must avoid undefined shifts; it handles single-word `numBits == 64`, and multi-word masks use `(end - 1) % 64`, but edge cases around zero-size keyspaces or invalid ranges would be dangerous. `std::vector<bool>` has proxy semantics, so benchmarking it against word operations is useful but not a drop-in production proof. Static deterministic workloads are reproducible but may underrepresent real transaction distributions.

Test signals: `CorrectnessTest/VerifyAllImplementations` is the main safety signal. Additional useful tests include boundary ranges crossing word boundaries, single-bit and full-word ranges, empty ranges, dense workloads, and realistic workload benchmark stability.
