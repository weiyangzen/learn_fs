# sources/storage-engines/rocksdb/port/util_logger.h

Purpose: selects a platform-specific logger implementation for low-level RocksDB port code.

Important APIs/types/functions: no direct API; on Windows it includes `port/win/win_logger.h`.

Control flow: compile-time include routing under `OS_WIN`.

State and persistence behavior: delegated to the included logger implementation.

Dependencies and integration points: lets code include one port logger header without hard-coding the Windows logger path.

Risks and test signals: unsupported platforms intentionally get no include from this file; build tests catch missing platform branches.
