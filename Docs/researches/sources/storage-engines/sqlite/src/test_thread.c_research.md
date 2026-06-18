# sources/storage-engines/sqlite/src/test_thread.c

## Purpose

`test_thread.c` is SQLite testfixture support for exercising database handles and SQLite APIs from Tcl-created threads. It is compiled only when `SQLITE_THREADSAFE` is true. The module registers a `sqlthread` Tcl command that can spawn a child Tcl interpreter in a new Tcl thread, open SQLite connections inside that thread, post scripts back to the parent event queue, and expose thread ids. On Unix builds with `SQLITE_ENABLE_UNLOCK_NOTIFY`, it also registers blocking wrappers around `sqlite3_step()` and `sqlite3_prepare_v2()` to demonstrate and test `sqlite3_unlock_notify()`.

## Important APIs, Types, And Functions

- `SqlThread` carries the parent `Tcl_ThreadId`, parent interpreter, child script, and parent result variable name for `sqlthread spawn`.
- `EvalEvent` subclasses `Tcl_Event` so a child thread can queue a script for evaluation in the parent interpreter.
- `tclScriptEvent()` evaluates queued event scripts and reports errors through `Tcl_BackgroundError()`.
- `postToParent()` copies a Tcl object script into an `EvalEvent` and alerts the parent thread.
- `tclScriptThread()` creates the child interpreter, registers test commands, runs the child script, posts either an error report and then a `set VARNAME result` script back to the parent, and exits the Tcl thread.
- `sqlthread_spawn()`, `sqlthread_parent()`, `sqlthread_open()`, and `sqlthread_id()` implement `sqlthread` subcommands.
- `clock_seconds_proc()` and `clock_milliseconds_proc()` provide testfixture clock commands independent of Tcl library script availability.
- Under Unix unlock-notify builds, `UnlockNotification`, `unlock_notify_cb()`, `wait_for_unlock_notify()`, `sqlite3_blocking_step()`, `sqlite3_blocking_prepare_v2()`, `blocking_step_proc()`, and `blocking_prepare_v2_proc()` implement blocking shared-cache lock waits.
- `SqlitetestThread_Init()` registers all Tcl commands in the parent test interpreter.

## Control Flow

`SqlitetestThread_Init()` installs `sqlthread`, clock helpers, and optionally unlock-notify Tcl commands. `sqlthread_proc()` dispatches validated subcommands. `sqlthread spawn VARNAME SCRIPT` copies both strings into one `ckalloc()` allocation, records the current Tcl thread and interpreter, and starts `tclScriptThread()` using `Tcl_CreateThread()`.

The child thread creates a fresh interpreter, installs SQLite/Tcl test commands (`Sqlitetest1_Init`, mutex tests, `Sqlite3_Init`, and the thread command itself), evaluates the supplied script, then packages the result into Tcl list scripts for the parent. If the script fails, it first posts `error <message>`, then posts `set <varname> <result>` so the parent can `vwait` the variable. The child frees its `SqlThread`, releases Tcl references, deletes its interpreter, drains pending events nonblocking, and calls `Tcl_ExitThread()`.

`sqlthread parent SCRIPT` is a one-way parent event queue helper. The file comments mark it as not currently working for synchronous result return: it queues and alerts the parent but does not wait for or propagate a parent evaluation result.

The unlock-notify path wraps SQLite calls that return `SQLITE_LOCKED`. `sqlite3_blocking_step()` retries `sqlite3_step()` after `wait_for_unlock_notify()` signals a pthread condition variable. `sqlite3_blocking_prepare_v2()` performs the same loop around `sqlite3_prepare_v2()`. Tcl wrappers convert pointer strings to SQLite handles/statements and return `sqlite3ErrName()` strings or statement pointer strings.

## State And Persistence Behavior

The file owns transient Tcl-thread state only. `SqlThread` and `EvalEvent` payloads are heap allocated with Tcl allocators and passed across Tcl thread queues. Results persist only as Tcl variables in the parent interpreter, not in SQLite database state.

`sqlthread_open()` creates a real SQLite connection, registers the MD5 extension function, and installs a busy handler that sleeps 50 ms and always retries. That connection persists until test scripts close it through other testfixture commands.

The unlock-notify sample allocates a stack `UnlockNotification` with a pthread mutex and condition variable for each wait. It uses SQLite's connection-level unlock-notify registration and destroys pthread primitives before returning.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, `tclsqlite.h`, Tcl threads/events, SQLite testfixture entry points, and test helpers from `test1.c`. The child interpreter deliberately initializes a subset of the testfixture so thread scripts can open databases, use mutex tests, and call normal SQLite Tcl commands. `sqlite3ErrName()` from SQLite core provides symbolic result names.

The unlock-notify code is guarded by `SQLITE_OS_UNIX && SQLITE_ENABLE_UNLOCK_NOTIFY` because it uses pthread condition variables. It is also embedded between documentation extraction comments for the `sqlite3_unlock_notify()` API sample, so changes can affect generated documentation as well as tests.

## Risks And Edge Cases

- The parent interpreter pointer is shared with queued events. The parent must remain alive and enter Tcl's event loop; otherwise queued scripts do not run and child-to-parent behavior can hang or target invalid state.
- `sqlthread_parent()` is explicitly incomplete for synchronous use. Tests should treat it as fire-and-forget.
- Child thread initialization must remain consistent with testfixture command dependencies; missing commands in child interpreters can cause thread-only test failures.
- `sqlthread_open()` ignores the return code from `sqlite3_open()` before registering MD5 and a busy handler, so tests using it must handle bad pointer or failed connection behavior carefully.
- The busy handler retries indefinitely, which is useful for concurrency tests but can hide deadlocks.
- Unlock-notify waits must handle `SQLITE_LOCKED` returned directly by `sqlite3_unlock_notify()` as a deadlock signal and must not retry in that case.
- Tcl object reference counts and cross-thread script copies are correctness-critical; queued `EvalEvent` data must outlive the posting thread.

## Test Signals

Useful tests spawn child scripts, wait with `vwait`, verify parent variables receive normal results and error results, and confirm `sqlthread id` differs between parent and child. Concurrency tests should open handles in multiple child threads, exercise busy-handler retry behavior, and ensure parent events drain. Unlock-notify tests should cover blocking and nonblocking prepare, blocking step, deadlock detection, statement reset before retry, and correct Tcl tail variable handling.
