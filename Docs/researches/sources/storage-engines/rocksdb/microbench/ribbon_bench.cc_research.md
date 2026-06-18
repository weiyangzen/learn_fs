# sources/storage-engines/rocksdb/microbench/ribbon_bench.cc

Purpose: Provides a focused Google Benchmark binary comparing fixed Bloom-like filter implementations, including Ribbon-related implementations, for build speed, positive query speed, negative query speed, filter size, and false positive percentage.

Important APIs/types/functions: `KeyMaker` generates unique-ish variable-length keys from `(filter_num, val_num)` using a reusable aligned buffer. `CustomArguments` enumerates every fixed filter implementation from `BloomLikeFilterPolicy::GetAllFixedImpls()` with bits-per-key, average key length, and entry-count combinations. `FilterBuild`, `FilterQueryPositive`, and `FilterQueryNegative` are registered benchmarks.

Control flow: Each benchmark constructs a `BloomLikeFilterPolicy`, wraps it in `mock::MockBlockBasedTableTester`, generates entries through `FilterBitsBuilder`, and then either times builder `AddKey`/`Finish` or times reader `MayMatch` calls. Negative queries use a different `filter_num` to avoid intentionally inserted keys and track false positives as a benchmark counter.

State and dependencies: State is in benchmark-local builders, readers, key buffers, and returned filter ownership (`owner`). It depends on internal block-based filter APIs and mock table helpers, not the full DB stack.

Risks/test signals: This is performance-only coverage. `KeyMaker::Get` invalidates previous slices because it reuses one buffer, which is safe for immediate builder/reader calls but unsafe if retained. The negative benchmark increments `i` without modulo; key generation still varies through encoded data but can wrap at `uint32_t`.
