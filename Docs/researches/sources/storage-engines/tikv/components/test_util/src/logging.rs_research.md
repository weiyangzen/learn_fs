# Research: sources/storage-engines/tikv/components/test_util/src/logging.rs

## sources/storage-engines/tikv/components/test_util/src/logging.rs

Purpose: custom synchronous slog logger for tests. It prefixes log lines with the test case tag, timestamp, file, line, level, message, and key-value pairs, writing either to `LOG_FILE` or stderr.

Important types are `Serializer`, `CaseTraceLogger`, and a local `Never` error type. `CaseTraceLogger::write_log` skips configured tags, derives the thread test tag via `tikv_util`, formats local time through `chrono`, serializes record and inherited KV pairs, writes a newline, and flushes. `init_log_for_test` is guarded by `Once`, reads `LOG_FILE`, `LOG_LEVEL`, and `LOG_APPEND`, disables noisy RocksDB/raftdb log tags and tokio targets, then initializes TiKV logging without async drain.

State and persistence are the optional log file mutex, global logger initialization, and environment-controlled append/truncate behavior. Dependencies are `slog`, `chrono`, `slog-global` through the crate root, `tikv_util::logger`, and standard IO.

Risks include synchronous flushing overhead, global one-time logger configuration, skipped tags hiding useful details, and reliance on thread names for case tags. Test signals are log output shape, absence of async logger tag loss, and downstream CI logs when `LOG_FILE` is set.
