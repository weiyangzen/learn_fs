# sources/object-store/garage/src/block/metrics.rs

Purpose: registers OpenTelemetry metrics for the block manager, including queue sizes, IO counters, resync outcomes, and corruption counts.

Important APIs/types/functions: `BlockManagerMetrics` struct and `BlockManagerMetrics::new`. Fields include value observers for compression level, RC size, resync queue length, errored blocks, and RAM buffer permits; counters/recorders for resync attempts/errors/duration/send/recv, bytes read/written, read semaphore timeouts, write/read durations, deletes, and corruptions.

Control flow: `new` binds meter instruments under meter name `garage_model/block`. Observer closures capture DB trees or semaphores and report current approximate values when scraped.

State and persistence: no persisted state. It observes persistent DB trees and runtime semaphore state.

Dependencies and integration points: depends on `opentelemetry`, `tokio::sync::Semaphore`, and `garage_db::Tree`. Constructed by `BlockManager::new`; updated throughout `manager.rs` and `resync.rs`.

Risks: observers call `approximate_len` and ignore failures; metrics can silently omit data when DB access fails. Metric names are part of monitoring contracts and should be changed carefully.

Test signals: no unit tests. Validation is compile-time plus runtime metrics scraping in deployments with telemetry enabled.
