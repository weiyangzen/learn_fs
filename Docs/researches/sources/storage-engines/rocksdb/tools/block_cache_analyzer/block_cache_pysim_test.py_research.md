<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py

## Purpose

`block_cache_pysim_test.py` is an executable test suite for the Python block-cache simulator. It uses assertions and synthetic traces rather than a test framework to validate hash-table operations, cache replacement behavior, hybrid row-key behavior, trace-observed hit accounting, and an end-to-end run across multiple cache factories.

## Important APIs, Types, And Functions

The test imports nearly every simulator-facing type from `block_cache_pysim.py`: cache implementations, policy implementations, `HashTable`, `CacheEntry`, `TraceRecord`, factory `create_cache()`, and driver `run()`.

`test_hash_table()` stress-tests insertion, replacement, deletion, lookup, `len()`, and uniqueness of `random_sample()` results. It maintains a Python dict as the oracle through one million random operations.

`assert_metrics()` is the core cache-state checker. It verifies `used_size`, access/miss counters, expected block keys, expected row keys, and entry sizes. It supports both the custom `HashTable` and normal dictionary-backed caches.

`test_cache()` builds a small sequence of repeated accesses to keys 1, 2, and 3, then inserts key 4 to check which key is evicted. `test_lru_cache()`, `test_mru_cache()`, and `test_lfu_cache()` specialize this shared sequence with expected outcomes.

`test_mix()` performs randomized access over a fixed key universe and validates high-level invariants: miss ratio is positive, trace cache mirrors trace hit bits, non-trace caches do not exceed capacity, and the sum of entry sizes equals `used_size`.

`test_end_to_end()` writes a synthetic `test_trace`, creates several cache types through `create_cache()`, calls `run()`, checks every cache processed `n` records, asserts OPT has no higher miss ratio than any other cache, and removes the generated trace file.

`test_hybrid()`, `test_opt_cache()`, and `test_trace_cache()` target row/block hybrid semantics, Belady MIN next-access eviction, and direct trace-observed hit behavior respectively.

## Control Flow

The file is designed for direct execution. Under `if __name__ == "__main__"`, it runs all test functions sequentially, then loops across many cache type strings and row-cache suffix modes to call `test_mix()`, and finally performs the synthetic end-to-end trace run.

Most tests mutate a shared `TraceRecord` object by changing selected fields between calls. This keeps setup compact and makes expected state transitions explicit. The randomized tests rely on Python's default random seed, so they cover many combinations but are not deterministic.

## State And Persistence Behavior

The only persistent artifact is the temporary `test_trace` file created by `test_end_to_end()`, which is removed on successful completion. If an assertion or runtime exception occurs before cleanup, the file may remain in the working directory.

Tests intentionally inspect internal cache state such as `used_size`, `table`, and policy data structures. This gives strong white-box coverage of simulator invariants but couples tests tightly to implementation details.

## Dependencies And Integration Points

The test depends on the importable sibling module `block_cache_pysim.py` and standard `os`, `random`, and `sys`. It does not use pytest/unittest discovery conventions. It can be run as `python3 block_cache_pysim_test.py` from the analyzer directory, assuming simulator dependencies such as numpy are installed.

It serves as the only direct validation signal for the simulator invoked by `block_cache_pysim.sh`; there is no direct integration test that runs the shell batch or plotting pipeline.

## Risks And Edge Cases

The test suite is expensive: `test_hash_table()` runs one million randomized operations, `test_mix()` runs 100k operations per cache/mode combination, and `test_end_to_end()` writes and processes 100k trace rows across multiple cache types. This is useful for stress but can be slow in lightweight CI.

Randomized tests are not seeded, so failures may be difficult to reproduce exactly. The tests also do not use `try/finally` around `test_trace` cleanup.

Because the simulator currently uses Python 2 comparison idioms in active cache paths, these tests may fail under Python 3 before reaching all intended assertions. The test file itself is therefore an important compatibility signal, not just a correctness signal.

The tests do not validate generated CSV file contents from `report_stats()`, policy timeline reporting, shell aggregation, plotting, malformed traces, target column-family filtering, or warmup reset behavior in detail.

## Test Signals

Positive signals include broad coverage of cache factory strings, row-key modes `0`, `1`, and `2`, exact expected evictions for small deterministic sequences, internal size accounting, and end-to-end trace replay. Gaps remain around output-file contracts and external orchestration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_pysim_test.py -->
