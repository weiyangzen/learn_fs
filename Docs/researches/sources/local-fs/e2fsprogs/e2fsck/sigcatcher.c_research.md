# File Research: sources/local-fs/e2fsprogs/e2fsck/sigcatcher.c

## Purpose
Implements e2fsck fatal signal diagnostics. It installs handlers for crash-like signals and prints signal names, `si_code` decoding, fault addresses, and optional backtraces before exiting with `FSCK_ERROR`.

## Main Elements
- `struct str_table`: maps numeric signal or `si_code` values to symbolic names.
- Signal/code tables: conditionally include platform-defined signal constants and signal-specific codes for `SIGILL`, `SIGFPE`, `SIGSEGV`, `SIGBUS`, and `SIGCHLD`.
- `lookup_table()` / `lookup_table_fallback()`: convert numeric values to names, falling back to decimal formatting.
- `die_signal_handler()`: `SA_SIGINFO` handler that reports signal metadata, optional `backtrace_symbols_fd()`, then exits.
- `sigcatcher_setup()`: registers the fatal handler for `SIGFPE`, `SIGILL`, `SIGBUS`, `SIGSEGV`, and `SIGABRT`.
- `DEBUG` test main: exercises abort, divide-by-zero, kill, null write, and sleep paths.

## Dependencies And Integration
Includes `e2fsck.h` for exit codes and attributes. Uses optional `<execinfo.h>` and `HAVE_BACKTRACE` for diagnostic stack output. Called early from `unix.c` main before parsing and filesystem work.

## Behavioral Notes
The handler uses stdio from a signal handler, which is diagnostic rather than async-signal-safe. It exits directly instead of trying to unwind e2fsck state, making it suitable for unexpected process faults rather than normal cancellation.
