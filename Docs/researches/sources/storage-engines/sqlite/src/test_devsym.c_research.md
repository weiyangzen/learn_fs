# sources/storage-engines/sqlite/src/test_devsym.c

## Purpose

`test_devsym.c` is a test-only VFS wrapper used to simulate device properties and abrupt process failure during writes. It registers `devsym` to override `xSectorSize` and `xDeviceCharacteristics`, and `writecrash` to abort the process on a configured write count while otherwise delegating to the real VFS.

## Important APIs, types, and functions

The central type is `devsym_file`, a `sqlite3_file` wrapper with the real file handle stored after it in the allocation. `struct DevsymGlobal g` stores the wrapped VFS, synthetic device flags, sector size, and crash countdown. Public entry points are `devsym_register()`, `devsym_unregister()`, and `devsym_crash_on_write()`. Most VFS/file methods delegate through `sqlite3Os*`; the key overrides are `devsymSectorSize()`, `devsymDeviceCharacteristics()`, and `writecrashWrite()`.

## Control flow

Registration lazily captures the default VFS, expands wrapper `szOsFile`, and registers both wrapper VFSes. Opens allocate the real file handle after the wrapper and install either `devsym_io_methods` or `writecrash_io_methods`. `writecrashWrite()` decrements `g.nWriteCrash` and calls `abort()` when it reaches zero, before the real write.

## State and persistence behavior

There is no independent persistent state; all durable work is delegated to the wrapped VFS. Runtime behavior is process-global and mutable through `g`, so tests must manage registration and crash-count lifecycle carefully.

## Dependencies and integration points

Compiled under `SQLITE_TEST`, it depends on `sqlite3.h`, `sqliteInt.h`, and SQLite VFS internals. Pager, journal, WAL, and crash-recovery tests use it through `vfs=devsym` or `vfs=writecrash`.

## Risks and test signals

Global state can interfere across concurrent tests, shared-memory calls assume version-2 real methods, and `writecrash` intentionally terminates the process. Signals are changed pager behavior under synthetic device flags and deterministic child-process aborts at configured write counts.
