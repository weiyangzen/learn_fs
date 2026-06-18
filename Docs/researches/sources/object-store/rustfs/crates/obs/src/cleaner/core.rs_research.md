<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/core.rs -->
# sources/object-store/rustfs/crates/obs/src/cleaner/core.rs

## Purpose
Implements the log cleanup service: scan matching logs, choose retention victims, optionally compress them, securely delete originals, expire old compressed archives, and emit metrics.

## Important APIs, Types, and Functions
`LogCleaner` is the immutable service object. `LogCleaner::builder` returns `LogCleanerBuilder`; `cleanup` runs one pass. Important internals include `select_files_to_process`, `select_expired_compressed`, `parallel_stealing_compress`, `serial_compress_and_delete`, `secure_delete`, and `delete_files`. The builder exposes retention, size, age, dry-run, exclusion, compression, zstd, and parallel-worker settings.

## Control Flow
`cleanup` exits early for missing directories, scans via `scanner::scan_log_directory`, sorts regular logs by modification time, selects files by keeping newest generations and enforcing size limits, then compresses/deletes either serially or with work-stealing workers. Compressed archives are separately expired by age. Metrics counters/histograms/gauges are emitted for deletion, freed bytes, compression duration, and stealing success.

## State and Persistence
The cleaner has no mutable in-memory state between passes. Persistent effects are deletion of selected files, optional archive creation, and deletion of expired archives. Dry-run returns projected counters without mutation.

## Dependencies and Integration
Uses scanner, compressor, cleaner types, crossbeam channel/deque/thread utilities, `metrics`, tracing, and global metric name constants. It is re-exported by `cleaner::mod` and likely used by telemetry rolling-log setup.

## Risks
Retention selection treats `keep_files` as a maximum retained count despite some comments saying minimum. Invalid glob patterns are silently ignored. Parallel compression falls back to serial only on worker panic, not on individual compression failures. Dry-run metrics may look like real deletion if consumers do not distinguish logs.

## Test Signals
Tests in `mod.rs` cover oldest deletion by size, keep-file enforcement, ignoring unrelated files, scanner counts, dry-run non-mutation, and suffix matching. Core also has explicit symlink refusal and Windows retry logic for deletion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/cleaner/core.rs -->
