# sources/storage-engines/sqlite/test/crashtest1.c

## Purpose
`crashtest1.c` is an older Unix-only crash-recovery stress program for rollback-journal behavior. It repeatedly kills child processes while they are inserting into a database, then expects subsequent opens to recover safely.

## Important APIs, Types, and Functions
- `do_some_sql()` opens `test.db` with the legacy SQLite 2 API (`sqlite_open`/`sqlite_exec_printf`), inserts random rows until an error, and kills the parent if corruption is detected.
- `main()` initializes `test.db`, forks 10,000 children, sleeps briefly, sends `SIGKILL`, and waits for each child.
- Unix APIs include `fork`, `kill`, `waitpid`, `access`, `unlink`, `system("cp ...")`, `usleep`, and `sched_yield`.

## Control Flow
The parent deletes old database and journal files, creates table `t1`, and then loops. Each child opens the database, possibly snapshots a pre-existing journal and database image for debugging, and inserts until interrupted or an SQLite error occurs. The parent kills the child after a randomized short delay, forcing recovery to happen on the next child open.

## State and Persistence Behavior
The persistent state is `test.db` plus rollback journals. The program also writes `test.db-saved` and `test.db-journal-saved` when it notices an existing journal before open, preserving evidence of a recovery-required state. Killed children intentionally leave dirty process state and possibly hot journals.

## Dependencies and Integration Points
This test targets legacy SQLite rollback recovery and Unix process semantics. It includes `sqlite.h` rather than modern `sqlite3.h`, so it is for older compatibility builds or historical test context.

## Risks and Edge Cases
Because it kills processes with `SIGKILL`, it is intentionally disruptive and should only run in a scratch directory. The `system("cp ...")` calls assume a Unix shell and `cp`. Detection is coarse: it terminates the parent on `SQLITE_CORRUPT` or malformed-image errors but otherwise mostly relies on repeated recovery opens.

## Test Signals
Normal progress prints `test N, pid=...` and child insert counts. Corruption or malformed database messages are failure signals, and the parent may be killed to preserve failing artifacts.
