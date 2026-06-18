# sources/storage-engines/sqlite/src/os.c

Purpose: implements common OS/VFS wrapper routines used by the SQLite core, independent of specific Unix/Windows/KV VFS backends. It centralizes `sqlite3_file` method dispatch, VFS registration, deterministic test hooks, and allocation wrappers.

Important APIs and state: `sqlite3OsClose/Read/Write/Truncate/Sync/FileSize/Lock/Unlock/CheckReservedLock/FileControl/FileControlHint/SectorSize/DeviceCharacteristics`, WAL shared-memory wrappers, mmap fetch/unfetch wrappers, VFS wrappers like `sqlite3OsOpen/Delete/Access/FullPathname/DlOpen/Randomness/Sleep/CurrentTimeInt64`, allocation helpers `sqlite3OsOpenMalloc()` and `sqlite3OsCloseFree()`, `sqlite3OsInit()`, `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()`. Test globals track simulated I/O errors, disk-full faults, VFS OOM tests, and open-file count.

Control flow: file wrappers call the corresponding `sqlite3_io_methods` entry with local guards such as no-op sync when flags are zero, fallback sector size, and disabled mmap stubs when `SQLITE_MAX_MMAP_SIZE<=0`. VFS wrappers mask invalid open flags before `xOpen`, set output paths to empty before `xFullPathname`, use deterministic PRNG seed output when configured, and fall back from `xCurrentTimeInt64` to `xCurrentTime`. VFS registration maintains a global linked list under `SQLITE_MUTEX_STATIC_MAIN`, unlinking existing instances before inserting as default or non-default.

State and persistence: global `vfsList` is the persistent process registry of VFS implementations. Test-only globals inject transient failures. No database bytes are persisted here; persistence is delegated to concrete VFS methods.

Dependencies and integration points: includes `sqliteInt.h`, relies on `sqlite3_vfs`, `sqlite3_file`, mutex subsystem, malloc subsystem, loadable-extension configuration, WAL/mmap compile flags, `sqlite3_os_init()` supplied by platform VFS files, and `sqlite3JournalIsInMemory()` to avoid some OOM injection against memory journals.

Risks: wrapper behavior is part of SQLite's internal ABI; changing return-code handling can affect pager correctness. Fault injection deliberately excludes some file-controls because simulated post-commit failures would confuse transaction tests. `sqlite3OsOpen()` masks flags with a hard-coded valid VFS flag mask. VFS list mutation must remain mutex-protected and autoinit-safe.

Test signals: run core I/O fault-injection suites with `SQLITE_TEST`; test VFS registration order and default selection; verify open flag masking; run WAL and mmap builds; test deterministic `iPrngSeed`; force malloc failure in `sqlite3OsInit()` and `sqlite3OsOpenMalloc()`; and verify time fallback for VFS iVersion 1.
