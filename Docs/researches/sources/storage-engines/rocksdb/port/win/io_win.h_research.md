# sources/storage-engines/rocksdb/port/win/io_win.h

Purpose: declares Windows low-level file wrappers and error helpers used by `WinFileSystem`.

Important APIs/types/functions: error conversion helpers, `pread`, `pwrite`, `fallocate`, `ftruncate`, `GetUniqueIdFromFile`, and all Windows file wrapper classes.

Control flow: class declarations separate common handle state (`WinFileData`), common random-read behavior (`WinRandomAccessImpl`), common write behavior (`WinWritableImpl`), and concrete RocksDB FS interfaces.

State and persistence behavior: declarations expose state fields for handles, alignment, mapping regions, file offsets, sync state, and file locks.

Dependencies and integration points: depends on `rocksdb/file_system.h`, `rocksdb/status.h`, `AlignedBuffer`, and Windows APIs. `env_win.cc` instantiates these classes.

Risks and test signals: inheritance is deliberately mixed private/protected/public; changes can break polymorphic FS behavior. Direct-I/O contract comments should be tested by file-writer and random-access tests.
