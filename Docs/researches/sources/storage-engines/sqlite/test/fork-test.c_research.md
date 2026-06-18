# sources/storage-engines/sqlite/test/fork-test.c

## Purpose
`fork-test.c` demonstrates and tests safe handling of SQLite database connections inherited across `fork()`, especially when the parent has an active write transaction. It verifies that the child can neutralize inherited file handles, close the inherited connection without rolling back the parent's transaction, then open its own connection and commit independent work.

## Important APIs, Types, and Functions
- Helpers: `whoAmI()`, `execCallback()`, `sqlExec()`, and `vfsTraceCallback()`.
- External integration: `vfstrace_register()` from `ext/misc/vfstrace.c`.
- Fork safety sequence: the child iterates database names with `sqlite3_db_name()`, applies `SQLITE_FCNTL_NULL_IO`, obtains the journal pointer with `SQLITE_FCNTL_JOURNAL_POINTER`, applies null I/O to the journal handle when possible, and then calls `sqlite3_close()`.
- CLI options: `--wal`, `--vfstrace`, `--commit-before-fork`, and `--delay-after-4`.

## Control Flow
The parent opens a new database, optionally switches to WAL, creates `t1`, inserts the first row, begins an immediate transaction, inserts the second row, and optionally commits before forking. After `fork()`, the child performs the special close procedure on the inherited connection and may pause. The parent sleeps briefly, commits if needed, and verifies rows. The child later opens a fresh connection, verifies parent-committed rows, inserts a third row, and exits. The parent waits and then verifies the third row.

## State and Persistence Behavior
The test uses a real database file named by the user and may create WAL/journal side files. Parent and child share inherited file descriptors immediately after fork, but the child is expected to avoid real I/O on inherited SQLite handles by using `SQLITE_FCNTL_NULL_IO` before close. Subsequent child writes use a new SQLite connection.

## Dependencies and Integration Points
This test depends on POSIX `fork`, `wait`, `sleep`, `unlink`, process IDs, SQLite file-control APIs, journaling/WAL behavior, and optional VFS tracing. It directly documents expected application behavior around forked processes.

## Risks and Edge Cases
Using inherited SQLite connections after fork is unsafe except for carefully constrained close/exec cases. The test exits on any SQLite error, so lock timing, WAL support, filesystem behavior, or unsupported file-controls can surface as failures. The option parser accepts both single- and double-dash forms after normalizing one leading dash.

## Test Signals
Expected output shows parent and child steps and query rows. Success means both processes see committed rows in order and no I/O/locking errors occur. VFS tracing can be enabled to inspect file-control and locking behavior.
