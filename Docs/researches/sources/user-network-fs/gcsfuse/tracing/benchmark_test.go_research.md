# sources/user-network-fs/gcsfuse/tracing/benchmark_test.go

Purpose: benchmarks tracing operations for both OpenTelemetry and noop tracer implementations.

Important APIs/types/functions: `BenchmarkTrace` with sub-benchmarks for span start/end, server span start/end, record error, trace upload with/without errors and bytes, set cache/upload attributes, and context propagation.

Control flow: iterates over `NewOTELTracer()` and `NewNoopTracer()`, runs `b.Run` sub-benchmarks, and loops with `b.Loop()` to exercise each tracing method.

State/persistence behavior: benchmark-only in-memory span operations; no persistent output except Go benchmark results.

Dependencies/integration: validates relative cost of the `TraceHandle` interface implementations.

Risks/test signals: recording errors repeatedly on one span in the benchmark differs from typical one-error-per-span usage but gives a stable microbenchmark target.
