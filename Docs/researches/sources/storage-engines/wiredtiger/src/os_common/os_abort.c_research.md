# sources/storage-engines/wiredtiger/src/os_common/os_abort.c

## Purpose
Centralizes process termination behavior for fatal WiredTiger errors and debug crash injection.

## Important APIs, Types, and Functions
`__wt_abort` logs an abort message, optionally waits for debugger attachment under `HAVE_ATTACH`, sends pending error logs to the event handler, and calls `abort`. `__wt_debug_crash` either calls `__wt_abort` on Windows or kills the process with `SIGKILL` elsewhere.

## Control Flow
`__wt_abort` is marked noreturn and exported. Under attach builds it logs the process ID and sleeps repeatedly; otherwise it logs a generic abort message. `__wt_debug_crash` chooses core-producing abort on Windows and non-core SIGKILL on POSIX-like systems.

## State and Persistence Behavior
There is no normal persistent state, but fatal termination can leave partial database state for recovery tests. Error logs are flushed to the configured handler before aborting.

## Dependencies and Integration Points
The file depends on signal/process APIs, `__wt_errx`, `__wt_error_log_to_handler`, and platform feature macros. It is used by panic, failpoint, diagnostic timeout, and crash-test paths.

## Risks and Edge Cases
`HAVE_ATTACH` can deliberately hang the process for debugger attachment. `SIGKILL` bypasses cleanup and handlers, which is useful for crash simulation but not for graceful fatal error reporting. Callers must treat both functions as terminal.

## Test Signals
Crash/recovery tests, panic injection, and debug crash tests validate that the process terminates in the expected mode and that recovery handles the resulting on-disk state.
