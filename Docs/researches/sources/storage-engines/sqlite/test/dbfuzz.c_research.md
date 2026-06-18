# sources/storage-engines/sqlite/test/dbfuzz.c

## Purpose
`dbfuzz.c` fuzz-tests SQLite database files. It loads each supplied database image into a custom in-memory VFS, opens it as `test.db`, extracts optional SQL from an `autoexec` table, appends `PRAGMA integrity_check`, and runs the SQL to look for crashes, assertion failures, leaks, and runaway VDBE programs without mutating the original disk file.

## Important APIs, Types, and Functions
- VFS state: `VFile`, `VHandle`, global `g.aFile[MX_FILE]`, `formatVfs()`, `reformatVfs()`, `findVFile()`, and `createVFile()`.
- VFS methods: `inmemOpen`, `inmemDelete`, `inmemAccess`, `inmemFullPathname`, `inmemRead`, `inmemWrite`, `inmemTruncate`, `inmemSync`, `inmemFileSize`, lock/unlock stubs, `inmemFileControl`, `inmemSectorSize`, and `inmemDeviceCharacteristics`, exposed through `VHandleMethods` and `inmemVfsRegister()`.
- SQL execution helpers: `Str` accumulator, `StrAppend()`, `integerValue()`, `sqlLog()`, `progressHandler()`, and `runSql()`.
- CLI options: memory heap limit, lookaside disable, timeout, trace/verbose output, and VDBE progress limit.

## Control Flow
`main()` parses options, optionally configures SQLite logging, heap, and lookaside, registers the in-memory VFS, and loops over input database paths. For each database, it sets an alarm if requested, loads the disk file into VFS file `test.db`, opens it with `sqlite3_open_v2(..., "inmem")`, optionally installs a progress handler, reads `SELECT sql FROM autoexec` into a script accumulator if that table exists, appends `PRAGMA integrity_check`, executes all statements with `runSql()`, closes the database, resets the VFS, frees script state, and checks `sqlite3_memory_used()`.

## State and Persistence Behavior
Disk input files are read-only from the fuzzer's perspective. All SQLite file I/O occurs in `g.aFile`, capped by `MX_FILE` and `MX_FILE_SZ`. Anonymous/delete-on-close files are reclaimed when their reference count drops to zero. `reformatVfs()` asserts no open references remain before freeing file buffers.

## Dependencies and Integration Points
The utility depends on SQLite's VFS API, `sqlite3_config()`, memory-status APIs, progress handlers, statement preparation/stepping/finalization, and optional Unix `alarm()`. It is designed to complement external database mutators and the `autoexec` convention used by SQLite fuzz corpora.

## Risks and Edge Cases
The VFS advertises safe append, undeletable-when-open, and powersafe-overwrite characteristics, so it does not model all real filesystems. `inmemRead()` must preserve short-read semantics by zero-filling buffers; any mistakes there could hide or invent corruption behavior. The fixed `MX_FILE` and `MX_FILE_SZ` limits can turn fuzz cases into `SQLITE_FULL`. `StrAppend()` uses SQLite allocation while other VFS buffers use libc allocation, so cleanup paths must keep allocators straight.

## Test Signals
Crashes, fatal timeouts, VDBE progress-limit panics, logged SQLite errors under verbose mode, nonzero close errors, and post-test memory leaks are failure signals. Successful runs exit 0 after all inputs are processed and all in-memory VFS state is freed.
