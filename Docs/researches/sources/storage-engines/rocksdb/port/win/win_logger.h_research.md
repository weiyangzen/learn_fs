# sources/storage-engines/rocksdb/port/win/win_logger.h

Purpose: declares the Windows implementation of RocksDB `Logger`.

Important APIs/types/functions: `WinLogger` constructor, `Flush`, `Logv`, `GetLogFileSize`, `DebugWriter`, and protected `CloseImpl`.

Control flow: the header defines the logger's public override surface; formatting and handle operations are implemented in `win_logger.cc`.

State and persistence behavior: stores a Win32 file handle and counters used to persist log output.

Dependencies and integration points: included by `util_logger.h` and `env_win.cc`, depends on `rocksdb/env.h` and `SystemClock`.

Risks and test signals: lifetime/close behavior matters because log files may be renamed/deleted while open. Logger and auto-roll tests are relevant.
