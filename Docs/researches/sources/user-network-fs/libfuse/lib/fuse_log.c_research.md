# sources/user-network-fs/libfuse/lib/fuse_log.c

## Purpose

`fuse_log.c` implements libfuse's small logging abstraction. It provides a default stderr logger, an optional syslog backend switch, and a public hook for applications or tests to replace the log sink.

## Important APIs, Types, And Functions

The file defines file-global `to_syslog` and `log_func` state. `default_log_func(enum fuse_log_level level, const char *fmt, va_list ap)` writes to `vsyslog` when syslog mode is enabled and otherwise writes to `stderr` with `vfprintf`.

Public functions are `fuse_set_log_func(fuse_log_func_t func)`, `fuse_log(enum fuse_log_level level, const char *fmt, ...)`, `fuse_log_enable_syslog(const char *ident, int option, int facility)`, and `fuse_log_close_syslog(void)`.

## Control Flow

`fuse_set_log_func` installs the provided callback, falling back to `default_log_func` when passed `NULL`. `fuse_log` creates a `va_list`, delegates to the current callback, and ends the list. `fuse_log_enable_syslog` sets `to_syslog` and calls `openlog`; `fuse_log_close_syslog` calls `closelog`.

## State And Persistence Behavior

State is process-global and in-memory. The current log function and syslog toggle affect every libfuse component using `fuse_log`. There is no file persistence in this implementation, though syslog mode emits to the host's syslog facility.

## Dependencies And Integration Points

The file includes `fuse_log.h` and depends on `<stdio.h>`, `<stdbool.h>`, `<syslog.h>`, and `<stdarg.h>`. It is used by most libfuse implementation files for diagnostics, including allocation failures, option warnings, clone-fd failures, module load failures, and debug traces in `fuse.c`.

## Risks And Edge Cases

There is no locking around `log_func` or `to_syslog`, so changing the log function or enabling syslog concurrently with logging is a data race in multithreaded filesystems. `fuse_log_close_syslog` does not reset `to_syslog`, so subsequent default logs still call `vsyslog` after `closelog`; many libc implementations tolerate this by reopening implicitly, but behavior is backend-dependent.

The defined `MAX_SYSLOG_LINE_LEN` is unused, so this implementation does not enforce a syslog line length cap. Custom log callbacks receive the live `va_list` and must consume it immediately.

## Test Signals

Tests should install a custom callback and assert that `fuse_log` forwards level, format, and arguments. A reset test should pass `NULL` to restore the default logger. Syslog tests can mock or intercept `openlog`, `vsyslog`, and `closelog`, and concurrency tests should document or expose the absence of synchronization around global logger state.
