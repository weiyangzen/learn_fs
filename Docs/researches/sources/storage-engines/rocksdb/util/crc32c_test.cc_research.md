# sources/storage-engines/rocksdb/util/crc32c_test.cc

Purpose: unit test executable for CRC-32C correctness across portable and accelerated implementations.

Important tests: `StandardResults` checks RFC 3720 vectors, deterministic buffer expected results for small aligned/unaligned and large inputs, and verifies incremental `Extend()` matches single-pass `Value()`. `Values`, `Extend`, `Mask`, `Crc32cCombineBasicTest`, `Crc32cCombineOrderMattersTest`, `Crc32cCombineFullCoverTest`, and `Crc32cCombineBigSizeTest` cover API properties and combine math.

Control flow: `main()` initializes GoogleTest and fills a large global buffer with deterministic FNV-derived 64-bit words before running tests. The expected table stores bitwise-inverted values for the three-way implementation checks, so tests compare `~expected.crc32c`.

State and persistence: uses global `buffer` and `expectedResults`. The tests assert stable persisted CRC behavior, mask transform behavior, and combine equivalence.

Dependencies and integration: includes `testharness`, `coding`, and `random`. It validates the implementation selected by build/runtime dispatch rather than directly selecting each backend.

Risks: architecture-specific code is only covered when the test binary runs on that architecture with those compile flags. Expected values are magic constants; failures need interpretation against CRC inversion conventions.

Test signals: this file itself is the strongest signal for CRC implementation correctness.
