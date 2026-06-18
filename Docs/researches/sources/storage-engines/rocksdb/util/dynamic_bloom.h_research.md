# sources/storage-engines/rocksdb/util/dynamic_bloom.h

Purpose: high-speed in-memory Bloom filter with optional lock-free concurrent insertion and batch lookup support.

Important APIs/types: `DynamicBloom` supports `Add`, `AddConcurrently`, `AddHash`, `AddHashConcurrently`, `MayContain`, batch `MayContain`, `MayContainHash`, and `Prefetch`. Internally, `DoubleProbe()` and templated `AddHash()` implement two bit probes per 64-bit word.

Control flow: keys are hashed with `BloomHash()`. `FastRange32()` maps the 32-bit hash to a base word, then `a ^ i` addresses subsequent double-probe words. A 64-bit golden-ratio multiply expands the hash; each iteration tests or sets two bits and rotates by 12 bits for the next pair. Batch lookup precomputes hashes and prefetches words before checking.

State and persistence: stores `kLen`, `kNumDoubleProbes`, and relaxed atomic word array. It is explicitly not serialized for compatibility. Concurrent adds use relaxed fetch-or to avoid races and lost bits but require external happens-before for visibility semantics.

Dependencies and integration: depends on `Slice`, `MultiGetContext`, `RelaxedAtomic`, `BloomHash`, `FastRange32`, and prefetch macros. It integrates with in-memory filters and multi-get lookup paths.

Risks: false-positive rate trades accuracy for speed; requires even `num_probes <= 10`. A poor or mismatched 32-bit hash would degrade distribution. Single-threaded `AddHash()` is not race-safe. Batch arrays assume `num_keys <= MultiGetContext::MAX_BATCH_SIZE`.

Test signals: `dynamic_bloom_test.cc` exercises correctness, false-positive thresholds, perf modes, and concurrent operations.
