# sources/storage-engines/rocksdb/logging/env_logger.h

Purpose: Logger implementation that writes formatted log records through a RocksDB `Env`/`FSWritableFile`.

Important APIs/types/functions: `EnvLogger`, `FileOpGuard`, `Logv`, `Flush`, `FlushLocked`, `CloseImpl`, `CloseHelper`, `GetLogFileSize`.

Control flow and state: `Logv` builds a timestamp/thread-id prefix, formats into a stack buffer and retries with a 64KB heap buffer if needed, appends a newline, then under `FileOpGuard` appends to `WritableFileWriter`, marks flush pending, and flushes if five seconds have elapsed. `FileOpGuard` disables perf/iostats pollution and locks the mutex for file operations. Close and flush also use the guard.

State and persistence behavior: appends to a log file and tracks pending flush plus last flush time. Close flushes/finishes the underlying writer. Reopening through factory can overwrite existing files depending on caller behavior.

Dependencies and integration points: `WritableFileWriter`, `Env`, `SystemClock`, perf/iostats context, port time functions, sync points used by auto-roll tests.

Risks: append errors are ignored and writer seen-error state is reset. `flush_pending_` and `last_flush_micros_` are atomic but most meaningful changes are mutex-guarded. Long messages beyond 64KB are truncated.

Test signals: `env_logger_test.cc` covers empty files, multiple lines, overwrite, close, and concurrent logging.
