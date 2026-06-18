# sources/storage-engines/foundationdb/flow/bench/BenchStream.cpp

Purpose: benchmarks `PromiseStream<StringRef>` send/receive throughput for different item counts and payload sizes.

Important APIs/types/functions: `benchStreamActor`, `bench_stream`, `getString`, `PromiseStream<StringRef>`, and `stream.getFuture()`.

Control flow: each iteration sends `items` copies of a prebuilt `StringRef` into the stream, then awaits and consumes the same number of futures.

State/persistence: one local stream is reused for the benchmark actor. Payload memory comes from `getString(size)` and is held for the actor lifetime.

Dependencies/integration: uses Flow streams/futures, network main-thread execution, TLS/network includes, and Google Benchmark.

Risks: producer and consumer are in the same coroutine and same thread, so results reflect in-memory stream buffering rather than cross-actor contention. The benchmark sends borrowed `StringRef` values, so payload lifetime must outlive receives, which it does locally.

Test signals: two-dimensional benchmark ranges cover item count and string size from 1 to `1 << 16`, with item count processed per iteration.
