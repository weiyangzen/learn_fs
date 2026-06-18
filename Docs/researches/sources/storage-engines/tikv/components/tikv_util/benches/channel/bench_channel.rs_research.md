# sources/storage-engines/tikv/components/tikv_util/benches/channel/bench_channel.rs

Purpose: benchmarks several channel implementations used or compared by `tikv_util`: standard library mpsc, TiKV utility mpsc, loose bounded TiKV mpsc, crossbeam, and future-stream receivers with and without batching.

Important APIs: benchmark functions are `bench_thread_channel`, `bench_util_channel`, `bench_util_loose`, `bench_crossbeam_channel`, `bench_receiver_stream_unbounded_batch`, and `bench_receiver_stream_unbounded_nobatch`. They use `test::Bencher`, `tikv_util::mpsc`, `crossbeam::channel`, and futures `StreamExt`.

Control flow: synchronous channel benchmarks spawn one receiver thread, run `b.iter()` sending one item per iteration, send sentinel `0`, join, and assert the sent count equals received count. Loose bounded sending spins on `try_send()` until accepted. Future-stream benchmarks spawn producer threads sending unbounded integers and repeatedly drain 10,000 items per bench iteration, either in batches of 32 or one item at a time.

State and persistence: state is in-memory counters, channel queues, and producer/consumer threads. No persistent output is written.

Dependencies and integration: compiled through the `channel` bench target in `Cargo.toml`; integrates with TiKV's custom `mpsc::future::BatchReceiver` and wake policies (`TillReach(8)` versus `Immediately`) to compare batching behavior.

Risks: producer threads in future benchmarks run until send fails and are not explicitly joined; benchmark results can be scheduler-sensitive. Spin loops in loose bounded tests measure retry overhead as part of send cost.

Test signals: assertions ensure no synchronous messages are lost. Bench harness performance output is the primary signal; future-stream benchmarks focus throughput rather than exact sent/received equality.
