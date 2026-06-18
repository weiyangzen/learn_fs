# sources/storage-engines/tikv/components/tikv_util/src/logger/mod.rs

## Purpose
Builds TiKV's slog-based logging backend, including global initialization, async guard management, file/terminal writers, text/JSON/RocksDB formats, dynamic log-level filtering, slow-log filtering, tag-based dispatch, and thread-id injection.

## Important APIs, Types, And Functions
`init_log` wires a drain into the global logger with level, async/sync mode, stdlog redirection, disabled targets, and slow-log threshold. `set_global_logger`, `exit_process_gracefully`, and `panic_after_best_effort_flush` manage global logger replacement and async flush behavior.

Writer/format constructors include `file_writer`, `term_writer`, `text_format`, `slow_log_text_format`, `rocks_text_format`, `json_format`, and `slow_log_json_format`. Level helpers include `get_level_by_string`, `get_string_by_level`, conversion between `slog::Level` and `log::Level`, `get_log_level`, and `set_log_level`.

Formatting and filtering types include `TikvFormat`, `RocksFormat`, `LogAndFuse`, `SlowLogFilter`, `GlobalLevelFilter`, `LogCost`, `LogDispatcher`, `ThreadIDrain`, and the text-field `Serializer`.

## Control Flow
`init_log` stores the initial atomic log level, extends disabled targets from `TIKV_DISABLE_LOG_TARGETS`, builds a module filter, then wraps the drain with slow-log filtering, thread-id injection, global level filtering, and optional `slog_async::Async`. Async mode stores an `AsyncGuard` in `ASYNC_LOGGER_GUARD`; sync mode wraps the drain in a mutex.

`TikvFormat::log` writes timestamp, level, source file/line, escaped message, record key-values, logger key-values, newline, and flushes. `RocksFormat` writes a RocksDB-like line and suppresses headers for tags ending in `_header`. `json_format` emits newline-delimited JSON with message, caller, level, and optional time.

`SlowLogFilter` inspects records tagged `slow_log`, extracts the `takes` field through `SlowCostSerializer`, and filters records with cost less than or equal to the threshold. `LogDispatcher` routes tags starting with `slow_log`, `rocksdb_log`, or `raftdb_log` to specialized drains, otherwise to the normal drain. `LogAndFuse` catches drain errors and logs the original record plus a critical logger-error message to stderr.

## State And Persistence
Global state is the atomic `LOG_LEVEL` and optional async logger guard. Persistent effects happen through configured writers, especially rotating file writers. `set_log_level` changes both TiKV's atomic filter and stdlog redirection.

## Dependencies And Integration
Depends on `slog`, `slog_async`, `slog_json`, `slog_term`, `slog_global`, `log`, `grpcio`, `chrono`, file logging helpers, TiKV thread wrappers, and config size/duration types. It is the backend for macros in `log.rs` and `macros.rs` and for subsystem-specific RocksDB/RaftDB/slow logs.

## Risks
Async logging can lose messages if the guard is not dropped, so explicit graceful exit and best-effort panic flush paths exist. `SLOG_CHANNEL_OVERFLOW_STRATEGY` is `Drop`, so overload can drop records. Dynamic level checks appear both in filters and formatters; inconsistent wrapping could change filtering behavior. Slow-log filtering only applies the threshold to exact `slow_log` tag records with a numeric `takes`; related tags or missing costs pass through. File writer rotation size is in MiB and rotation occurs on flush.

## Test Signals
Tests validate text and JSON formats, datetime parsing, source-file matching, global level filtering, level string/conversion helpers, unified level names, and dispatcher/slow-log filtering behavior across normal, slow, RocksDB, and RaftDB buffers.
