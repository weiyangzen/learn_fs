# sources/storage-engines/rocksdb/port/win/env_default.cc

Purpose: defines `Env::Default()` for Windows and initializes RocksDB process-wide helper singletons before constructing the default Windows environment.

Important APIs/types/functions: `Env::Default`, internal `winenv_once_flag`, and `envptr`.

Control flow: `Env::Default()` initializes thread-local, compression-context, and sync-point singletons, then uses `std::call_once` to allocate one `port::WinEnv`.

State and persistence behavior: intentionally leaks the default `WinEnv` instead of destroying it, avoiding loader-lock deadlocks when statics are torn down while background threads may be live. No files are persisted.

Dependencies and integration points: ties `WinEnv` into RocksDB's global `Env` API. It depends on `ThreadLocalPtr`, `CompressionContextCache`, sync-point singletons, and `port/win/env_win.h`.

Risks and test signals: singleton initialization order matters. Env tests, sync-point tests, and Windows DLL/static-destruction scenarios are relevant.
