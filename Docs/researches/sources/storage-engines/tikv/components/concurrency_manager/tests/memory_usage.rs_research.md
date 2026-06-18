# sources/storage-engines/tikv/components/concurrency_manager/tests/memory_usage.rs

Purpose: ignored, manual stress tests for memory behavior of the concurrency manager lock table and the forked crossbeam skiplist range iterator.

Important APIs and types: `test_memory_usage` and `stress_skipmap_range_iter`.

Control flow: `test_memory_usage` creates a huge number of random short keys across eight threads, inserts locks into a `ConcurrencyManager`, leaks guards to retain them, and prints allocator stats. `stress_skipmap_range_iter` repeatedly inserts, range-iterates, and removes keys in multiple threads while a monitor prints operation count, map length, and jemalloc allocated bytes, then observes idle memory reclamation.

State and persistence: in-memory only. Both tests intentionally retain or churn substantial memory and print diagnostics rather than asserting exact memory budgets.

Dependencies and integration: uses `tikv_alloc::fetch_stats`, `crossbeam_skiplist::SkipMap`, random keys, std threads, transaction locks, and futures `block_on`.

Risks: ignored tests are not CI daily coverage. The first test intentionally leaks guards, so it measures retained lock-table overhead rather than normal lifecycle cleanup. Memory figures depend on jemalloc and release-mode behavior.

Test signals: useful for regression investigation around lock-table amplification and skiplist range iterator leaks; not a deterministic correctness suite.
