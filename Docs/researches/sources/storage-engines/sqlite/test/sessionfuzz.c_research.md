# sources/storage-engines/sqlite/test/sessionfuzz.c

## Purpose

`sessionfuzz.c` fuzz-tests SQLite’s session/changeset module. It can generate seed changesets or apply fuzzed changesets, including SQL Archive batches, against a deterministic in-memory database while checking for crashes, integrity failures, and memory leaks.

## Important APIs, Types, and Functions

The file includes `sqlite3.c` with debug, session, preupdate hook, and deserialize support enabled. `zFillSql` populates base tables with varied values. `aDbBytes[]` embeds the base DB. Important helpers are `sqlarUncompressFunc()`, `runSql()`, `writeFile()`, `readFile()`, `makeChangeset()`, `db_reset()`, `fileTail()`, and `conflictCall()`. Session APIs include `sqlite3session_create()`, `sqlite3session_attach()`, `sqlite3session_changeset()`, `sqlite3session_delete()`, and `sqlite3changeset_apply()`.

## Control Flow

`main()` opens a `memdb` in-memory DB and resets it from `aDbBytes`. In `setup` mode, it fills tables, starts a session, attaches all tables, performs modifications, and writes cumulative seed changesets `c1.txt`, `c2.txt`, and `c3.txt`. In `run` mode, ordinary files are read as changesets, applied inside `BEGIN`/`ROLLBACK`, and reported by return code. SQLite-looking inputs are treated as SQL Archives: the archive is deserialized read-only, `sqlar_uncompress()` is registered, entries from `sqlar` are applied one at a time inside rolled-back transactions, and case counts are printed. Finally, it runs `PRAGMA integrity_check` and checks `sqlite3_memory_used()`.

## State and Persistence Behavior

The primary DB is in memory. `setup` persists `c1.txt`, `c2.txt`, and `c3.txt`. `run` rolls back every applied changeset, so fuzz cases should not persist changes. SQL Archive buffers are owned by the deserialized archive DB in that branch; ordinary changeset buffers are freed explicitly.

## Dependencies and Integration Points

It depends on SQLite session/preupdate/deserialize support, debug assertions, and optional zlib. It is designed for AFL-style workflows: seed generation, fuzz execution with `@@`, corpus minimization, and SQL Archive replay.

## Risks and Test Signals

All conflicts are omitted, emphasizing robustness over conflict-resolution semantics. SQL Archive detection is heuristic. zlib omission reduces compressed-archive coverage. Ownership of `pChgset` differs between ordinary and SQL Archive paths. Signals are creation of seed files, per-case return codes or archive case counts, `PRAGMA integrity_check` staying `ok`, no crashes/assertions, and zero SQLite memory usage.
