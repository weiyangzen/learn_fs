# sources/storage-engines/sqlite/test/c/changeblob1.c

## Purpose
`changeblob1.c` is a tiny C API regression test for the session/changegroup extension. It verifies that `sqlite3changegroup_change_blob()` handles an enormous blob length by returning an out-of-memory error instead of reading the small caller buffer or succeeding incorrectly.

## Important APIs, Types, and Functions
The test uses `sqlite3_open`, `sqlite3_exec`, `sqlite3changegroup_new`, `sqlite3changegroup_schema`, `sqlite3changegroup_change_begin`, `sqlite3changegroup_change_int64`, `sqlite3changegroup_change_blob`, `sqlite3changegroup_delete`, and `sqlite3_close`. It is compiled conditionally under `SQLITE_ENABLE_SESSION`.

## Control Flow
When sessions are enabled, the program creates an in-memory table, initializes a changegroup for `main`, starts an insert change for table `t1`, writes an integer primary-key field, fills a 64-byte buffer, then calls `sqlite3changegroup_change_blob()` with a length of `2147483647`. It returns success only if the API returns result code 7 (`SQLITE_NOMEM`). Without session support, it exits successfully without testing anything.

## State and Persistence Behavior
All database state is in-memory. The changegroup owns transient change-construction state and is deleted before close. The caller buffer is heap allocated and freed after the blob call.

## Dependencies and Integration Points
This is a public C API test for the session extension and changegroup builder. It relies on SQLite result-code numbering and the schema registered with `sqlite3changegroup_schema()`.

## Risks and Edge Cases
The test intentionally passes a length far larger than the allocated buffer. The expected behavior is early allocation/size failure without consuming the claimed amount of data. If result codes change or extended result codes are introduced in this path, the hard-coded `rc==7` check would be brittle compared with `SQLITE_NOMEM`.

## Test Signals
Exit status 0 means the oversized blob path returned `SQLITE_NOMEM`. Exit status -1 means the blob API accepted, rejected with an unexpected code, or otherwise failed the regression condition.
