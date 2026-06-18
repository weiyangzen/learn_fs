# sources/storage-engines/wiredtiger/test/thread/file.c

## Purpose

`file.c` provides table/file creation and initial bulk-load support for the `test/thread` stress executable.

## Important APIs, Types, and Functions

It defines static `file_create(const char *name)` and exported `load(const char *name)`. It uses global `conn`, `ftype`, and `nkeys` from `thread.h`.

## Control Flow

`file_create` opens a session, builds a row-store (`key_format=u`) or variable-record (`key_format=r`) create config with page-size settings, creates the object tolerating `EEXIST`, and closes the session. `load` calls `file_create`, opens a bulk cursor, iterates keys from 1 to `nkeys`, formats row-store keys as zero-padded byte strings or record-number keys, formats values, inserts them, and closes the session.

## State and Persistence Behavior

It creates and populates WiredTiger file objects named by callers, usually `file:wt.%03d`. Bulk-load data forms the starting state for concurrent readers/writers.

## Dependencies and Integration Points

Depends on `thread.h`, global test options, WiredTiger sessions/cursors, `testutil_snprintf_len_set`, and `testutil_check`.

## Risks and Edge Cases

The code assumes a global open connection. Bulk cursor failure or duplicate object handling is fatal except `EEXIST` during create.

## Test Signals

Signals are successful creation, full initial load of `nkeys`, and later verification by `rw_start`.
