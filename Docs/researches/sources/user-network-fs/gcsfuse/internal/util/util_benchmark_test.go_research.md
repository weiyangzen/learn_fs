## sources/user-network-fs/gcsfuse/internal/util/util_benchmark_test.go

Purpose: Benchmarks `BytesToHigherMiBs`.

Important APIs/types/functions: `BenchmarkBytesToHigherMiBs` repeatedly converts one MiB in bytes.

Control flow: uses Go benchmark `b.Loop()` and discards result.

State and persistence behavior: no state.

Dependencies and integration points: protects performance of a conversion helper likely used in hot-ish configuration/accounting paths.

Risks: only one input size is benchmarked; overflow and non-aligned cases are not benchmarked.

Test signals: benchmark-only, no correctness assertions.
