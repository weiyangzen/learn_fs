# sources/storage-engines/rocksdb/port/win/win_logger.cc

Purpose: implements RocksDB's Windows logger over a Win32 file handle.

Important APIs/types/functions: `WinLogger::Logv`, `Flush`, `CloseImpl`, `CloseInternal`, `DebugWriter`, and `GetLogFileSize`.

Control flow: `Logv` formats timestamp, microseconds, and thread id into a stack buffer, retries with a 30KB heap buffer if needed, appends a newline, and writes with `WriteFile`. Flush updates timing state but does not force disk flush except on close.

State and persistence behavior: owns a log file handle, atomic log size, last flush timestamp, and flush-pending flag. Close flushes file buffers and closes the handle.

Dependencies and integration points: created by `WinFileSystem::NewLogger`; uses `GetTimeOfDay`, `SystemClock`, `IOSTATS_TIMER_GUARD`, and Windows error formatting.

Risks and test signals: partial writes only assert in debug; `log_size_` adds intended write size when bytes were written. Auto-roll logger and env logger tests are primary signals.
