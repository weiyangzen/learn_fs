# sources/storage-engines/rocksdb/util/dynamic_bloom.cc

Purpose: constructor implementation for `DynamicBloom`, allocating and aligning the in-memory Bloom bit array.

Important functions: local `roundUpToPow2()` supports layout sizing. `DynamicBloom::DynamicBloom()` validates probe count, computes block size/bit rounding so XOR-offset double probes stay in range, allocates aligned memory through an `Allocator`, zeroes it, then adjusts `data_` to a block boundary.

Control flow: `num_probes` must be even and at most 10. Total bits are rounded up to whole probe-safe blocks. Allocation includes padding for alignment correction. Debug builds assert last-word XOR probes remain in range.

State and persistence: initializes immutable `kLen`, `kNumDoubleProbes`, and zeroed `RelaxedAtomic<uint64_t>* data_`. The filter is explicitly in-memory only and not schema/persistence stable.

Dependencies and integration: uses `memory/allocator.h`, `port/port.h`, `rocksdb/slice.h`, and hash utilities. Called by table/plain-table and memory-resident filter code.

Risks: requires non-null allocator and enough memory. Constructor uses asserts rather than runtime errors for invalid probe counts. Alignment math is integral to preventing out-of-bounds XOR probe offsets.

Test signals: `dynamic_bloom_test.cc` covers empty/small filters, false-positive behavior, and concurrent add/query behavior.
