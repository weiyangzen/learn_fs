# sources/object-store/rustfs/crates/io-core/src/pool.rs

Purpose: tiered reusable `BytesMut` buffer pool to reduce allocation churn in zero-copy-ish I/O paths.

Important APIs/types: `BytesPool` owns small, medium, large, and xlarge `PoolTier`s plus shared `BytesPoolMetrics`. `BytesPoolConfig` configures per-tier buffer sizes and max concurrent buffers. `PooledBuffer` derefs to `BytesMut` and returns its buffer to the tier on drop. Public methods include `new_tiered`, `with_config`, async `acquire_buffer`, nonblocking `try_acquire_buffer`, `metrics`, `hit_rate`, and `available_buffers`.

Control flow: size selection uses fixed thresholds: <=64 KiB small, <=512 KiB medium, <=4 MiB large, otherwise xlarge. A tier uses a Tokio semaphore to bound concurrent buffers, pops from `available_buffers` when possible, clears/reserves reused buffers, otherwise allocates `BytesMut::with_capacity(max(requested, tier_size))`. Drop takes the `ManuallyDrop<BytesMut>` and returns it to the tier if there is one, retaining it while the available vector is below `max_buffers`; otherwise the buffer is dropped and current allocated byte counters are decremented.

State and persistence: all state is in memory: semaphores, available buffer vectors protected by mutexes, and atomic metrics. Metrics are also emitted through `rustfs_io_metrics`.

Dependencies and integration: uses `bytes::BytesMut`, Tokio semaphore permits, atomics/mutexes, and `rustfs-io-metrics`. Re-exported from `lib.rs`.

Risks: `available_buffers` metric increments on return but is not decremented on take, so it can overstate currently available buffers. Async acquire falls back to an unpooled buffer if the semaphore is closed and does not record normal metrics for that path. Holding the metrics mutex only to unwrap an Arc adds overhead without much protection. Returned buffers keep their capacity, which improves reuse but can retain large memory in a tier.

Test signals: tests cover tier defaults, capacity selection, semaphore-closed fallback, try-acquire capacity failure, metrics presence, hit rate, available buffer count, reuse without additional allocation, allocated byte tracking, and tier hit counters.
