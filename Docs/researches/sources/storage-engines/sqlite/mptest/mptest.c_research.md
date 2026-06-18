# sources/storage-engines/sqlite/mptest/mptest.c

## Purpose

`mptest.c` is a standalone SQLite multiprocess test harness. It executes a custom script language against a shared SQLite database and starts child client processes so independent OS processes concurrently read and write the same database. The harness is designed to stress locking, busy handling, journal modes, WAL behavior, crash-like exits, and VFS behavior.

## Important APIs, Types, and Functions

The file uses the public SQLite C API: `sqlite3_open_v2`, `sqlite3_close`, `sqlite3_exec`, `sqlite3_prepare_v2`, `sqlite3_step`, `sqlite3_finalize`, `sqlite3_busy_handler`, `sqlite3_busy_timeout`, `sqlite3_create_function`, `sqlite3_enable_load_extension`, `sqlite3_trace`, `sqlite3_config(SQLITE_CONFIG_LOG)`, `sqlite3_file_control(SQLITE_FCNTL_VFSNAME)`, compile-option and source-id APIs, and SQLite allocation/formatting helpers.

Important local types and helpers include the global `g` struct for process-wide state, the dynamic `String` accumulator, `strglob()` for test-pattern matching, `printWithPrefix()`, `errorMessage()`, `fatalError()`, `logMessage()`, `busyHandler()`, `sqlTraceCallback()`, `sqlErrorCallback()`, `prepareSql()`, `runSql()`, `trySql()`, `evalSql()`, `evalFunc()`, `vfsNameFunc()`, `startScript()`, `finishScript()`, `startClient()`, `readFile()`, tokenizer helpers (`tokenLength`, `extractToken`, `findEnd`, `findEndif`), `waitForClient()`, `runScript()`, option parsing helpers, and `main()`.

## Control Flow

`main()` parses `DATABASE ?OPTIONS? ?SCRIPT?`, rejects script-looking database names, validates that the linked library and header source IDs match, opens logs, configures SQLite logging, and opens the database. The supervisor process deletes and recreates the test database, creates coordination tables (`task`, `counters`, `client`), reads the script, and runs it one or more times. Client processes are started with `--client N`, connect to the same database, claim tasks from `task`, execute their script fragments, and record completion.

Script execution alternates between raw SQL and meta-commands. SQL text accumulated before a command is evaluated and captured into `sResult` for assertions. Supported commands include sleeps, process exits, test-case markers, explicit finish, result reset/output, exact and glob assertions, nested script sourcing, printing, conditional blocks, client start/wait, task assignment, breakpoint, and SQL-error display toggling. Supervisor-only `--task` blocks insert work into the shared `task` table and ensure a client process exists. Clients claim work with `BEGIN IMMEDIATE`, update counters, honor `wantHalt`, mark task start/end timestamps, then loop.

## State and Persistence Behavior

The test database is both the subject under test and the scheduler. Persistent coordination tables store queued task text, client IDs, start/end times, halt requests, and aggregate error/test counters. The supervisor removes the database before starting, unless running as a client. Child startup uses shell backgrounding on Unix and `CreateProcessA` on Windows, so client lifetime is external to the supervisor process.

Global state controls tracing, SQL trace, error suppression, busy timeout, VFS name, database filename, log files, sync mode, task identity, and accumulated error/test counts. `fatalError()` attempts to update `client.wantHalt` before exit so other processes stop. `--exit N` can exit without `sqlite3_close()` when `N>0`, simulating a process crash after optional task-finish marking. Journal mode and synchronous mode are set by options, allowing the same script to test DELETE, WAL, PERSIST, TRUNCATE, and no-sync configurations.

## Dependencies and Integration Points

The harness depends on `sqlite3.h` and a SQLite object/library built with compatible `SQLITE_SOURCE_ID`. It uses standard C library headers plus POSIX `unistd.h` or Windows process APIs. The makefile builds it as `mptester$(T.exe)` and the `mptest` target runs bundled scripts such as `crash01.test` and `multiwrite01.test` under several journal modes. The script language exposes `vfsname()` and `eval()` SQL functions to tests, and integrates with SQLite's global error log callback.

## Risks and Edge Cases

Concurrency correctness is intentionally sensitive: scheduler tables are updated through a database that is also under locking stress, so busy-handler behavior and timeouts affect both test orchestration and test subject. The supervisor waits with fixed timeouts and reports errors if clients stall. `startClient()` builds command lines with quoted database and VFS names, but still uses `system()` on Unix, so unusual executable paths or shell metacharacters are a portability concern. The script tokenizer is custom and supports comments, strings, semicolon boundaries, nested `--if`, and `--task` blocks; malformed or unusual quoting can affect line accounting and command extraction.

Windows behavior differs for process spawning and for unsupported PERSIST/TRUNCATE journal-mode requests, which are coerced to DELETE. `readFile()` reads whole scripts into memory and assumes `ftell()`/`fread()` success. `tokenLength()` string handling and glob matching are test-language infrastructure, so bugs there can create false positives or false failures independent of SQLite itself.

## Test Signals

The harness reports `Summary: N errors out of M tests` and returns nonzero if errors were accumulated. Positive signals are successful exact `--match` and pattern `--glob` assertions, task completion timestamps, clients shutting down after `wantHalt`, and absence of timeouts or SQLite error-log events. The `main.mk` `mptest` target is the canonical integration signal because it repeats crash and multi-writer scripts under several journal modes.
