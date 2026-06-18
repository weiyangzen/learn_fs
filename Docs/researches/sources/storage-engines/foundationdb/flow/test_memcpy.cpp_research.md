# sources/storage-engines/foundationdb/flow/test_memcpy.cpp

Purpose: This Flow unit test validates the active `memcpy` implementation, including FoundationDB's included `rte_memcpy.h` and optionally `folly_memcpy.h`, across many sizes and source/destination alignments. It is a correctness guard for optimized memory-copy code used in performance-sensitive paths.

Important APIs and functions: `test_single_memcpy(off_src, off_dst, size)` fills aligned stack buffers with deterministic random data, calls `memcpy`, and verifies the return pointer plus copied and untouched regions. The `TEST_CASE("/rte/memcpy")` Flow unit test iterates all offsets from `0` to `31` and a fixed set of packet-like buffer sizes up to `8192`.

Control flow: For each alignment pair and size, the test initializes `src` and zeroes `dest`, performs the copy, checks bytes before the destination offset, checks each copied byte, and checks bytes after the copy range. Any mismatch prints a detailed failure and returns `-1`; the unit test asserts success.

State and persistence behavior: There is no persistent state. Runtime data is stack-allocated `uint8_t` buffers sized by `SMALL_BUFFER_SIZE + ALIGNMENT_UNIT`; randomness comes from Flow's deterministic random generator so failures are reproducible.

Dependencies and integration points: The file depends on Flow's unit-test framework, deterministic random support, and the chosen compile-time memcpy headers. It can be forced into the binary through `forceLinkMemcpyTests()`, which matters when unit-test registration depends on link inclusion.

Risks: The test checks non-overlapping copies only and does not validate `memmove` semantics. The post-copy bounds check assumes the configured largest buffer size is no larger than `SMALL_BUFFER_SIZE`; changing `TEST_VALUE_RANGE` or the size list must keep that invariant. Test signals are exact byte comparisons for all size/alignment combinations and the returned pointer contract.
