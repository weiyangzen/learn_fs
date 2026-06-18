# sources/storage-engines/rocksdb/port/win/port_win.cc

Purpose: implements Windows equivalents for RocksDB's POSIX-style port primitives.

Important APIs/types/functions: UTF-8/UTF-16 conversion, `GetTimeOfDay`, `CondVar::Wait/TimedWait`, `PhysicalCoreID`, `InitOnce`, `opendir/readdir/closedir`, `truncate`/`Truncate`, `Crash`, `ImmediateExit`, `GetMaxOpenFiles`, `SetCpuPriority`, `GetProcessID`, and `GenerateRfcUuid`.

Control flow: condition variables adopt an already-held mutex and release ownership before returning. Directory iteration wraps `FindFirstFileEx` and `FindNextFile`. Truncation opens an existing file and calls `SetFileInformationByHandle`. UUID generation uses RPC UUID APIs.

State and persistence behavior: directory objects own find handles; truncation mutates files; crash aborts; immediate exit calls `_exit`; UUID generation returns an RFC-style string. CPU priority is a no-op.

Dependencies and integration points: used by `port_win.h`, Windows Env, logger time code, and generic RocksDB code expecting POSIX-like APIs.

Risks and test signals: condition-variable absolute-time conversion must match RocksDB timed wait expectations. Directory iteration and truncation error mapping are compatibility-sensitive. Port, Env, file-lock, and timing tests are relevant.
