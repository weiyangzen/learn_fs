## sources/user-network-fs/gcsfuse/internal/util/sizeof_bench_test.go

Purpose: Benchmarks `UnsafeSizeOf` for common input categories.

Important APIs/types/functions: `BenchmarkUnsafeSizeOf_Int`, `BenchmarkUnsafeSizeOf_String`, and `BenchmarkUnsafeSizeOf_MinObject`.

Control flow: each benchmark constructs one value, resets timer, and repeatedly calls `UnsafeSizeOf`.

State and persistence behavior: no state or I/O.

Dependencies and integration points: validates performance expectation for low-overhead memory accounting helpers.

Risks: only benchmarks raw-size helper, not nested size functions where more work occurs.

Test signals: benchmark-only file; no correctness assertions.
