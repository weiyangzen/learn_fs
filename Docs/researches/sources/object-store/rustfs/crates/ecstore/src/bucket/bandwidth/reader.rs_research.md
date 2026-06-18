# sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/reader.rs

Purpose: `AsyncRead` wrapper that enforces bucket/replication bandwidth limits and updates bandwidth measurements as bytes are read.

Important APIs and types: `BucketOptions` is the hashable key (`name`, `replication_arn`). `MonitorReaderOptions` carries bucket options and `header_size`, allowing header bytes to consume tokens before body IO. `MonitoredReader<R>` wraps an inner reader, monitor, wait state, and reusable temporary buffer.

Control flow: `poll_read` first honors any pending sleep. If no throttle exists, it delegates directly. With a throttle, it computes allowed body bytes and token consumption via `calc_need_and_tokens`, consumes tokens, sleeps for deficit/rate when needed, then calls `poll_limited_read` so the inner reader cannot fill more than the permitted byte count. Successful body reads update the monitor measurement.

State and persistence: all state is in-memory reader-local plus monitor maps. No persistence.

Dependencies and integration points: integrates Tokio `AsyncRead`, `ReadBuf`, `Sleep`, the bandwidth `Monitor`, and replication target reads that need throttling.

Risks: `poll_read` can return ready with zero bytes for header-only token consumption, which callers must tolerate. Mutex poisoning is recovered. Ratelimit behavior depends on `Monitor::throttle` returning up-to-date cloned throttle state.

Test signals: unit tests cover passthrough, limited reads, header-only accounting, full throttled reads, header depletion, and one-byte/sec limits.
