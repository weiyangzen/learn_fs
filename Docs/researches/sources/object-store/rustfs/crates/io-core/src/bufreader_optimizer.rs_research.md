# sources/object-store/rustfs/crates/io-core/src/bufreader_optimizer.rs

Purpose: helper for choosing `tokio::io::BufReader` capacities and tracking buffering statistics.

Important APIs/types: `BufReaderConfig` configures max layers and small/large buffer sizes. `BufReaderStats` stores atomic totals for readers, eliminated layers, and buffer size adjustments. `BufReaderOptimizer` provides `optimal_buffer_size`, `optimize`, `stats`, `config`, `is_buffered_source`, and `eliminate_redundant_layers`. `BufferedSource` is a marker trait for sources considered already buffered.

Control flow: `optimal_buffer_size` chooses the large buffer when `data_size >= large_file_threshold`, otherwise the small buffer. `optimize` increments `total_readers` and returns `BufReader::with_capacity`. Redundant-layer removal is currently a no-op that returns the reader unchanged.

State and persistence: only in-memory atomic counters; no persistence. The optimizer is immutable after construction except stats.

Dependencies and integration: uses Tokio `AsyncRead` and `BufReader`, and is re-exported from `lib.rs`. It is intended for data paths deciding whether/how much to buffer around async readers.

Risks: `max_layers`, `buffer_size_adjustments`, and `eliminated_layers` are not functionally used yet, so the module name overstates current behavior. The marker trait can only prove buffering for types that explicitly implement it; there is no runtime detection of existing `BufReader` layers.

Test signals: tests cover default/custom config, small/large/unknown size decisions, actual async read through an optimized reader, and total reader stat tracking.
