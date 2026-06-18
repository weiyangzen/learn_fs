# sources/storage-engines/wiredtiger/test/format/format_util.c

Purpose: supplies common runtime utilities for progress display, path setup, lock abstraction, diagnostic page dumps, numeric parsing, wrapped session lifecycle, and session prefetch selection.

Important APIs and functions: `track_ops`, `track`, `path_setup`, `fclose_and_clear`, `lock_init`, `lock_destroy`, `cursor_dump_page`, `table_dump_page`, `set_core`, `atou32`, `wt_wrap_open_session`, `wt_wrap_close_session`, and `session_prefetch_cfg`.

Control flow: progress helpers render single-line operation counts and timestamp movement unless `GV(QUIET)` is set. Path setup fills `g.home*` paths. Lock helpers choose WiredTiger rwlocks or pthread rwlocks from config. Page dump helpers open a cursor, position by table type, and, in diagnostic builds, catch dump crashes via `sigsetjmp` around `__wt_debug_cursor_page`. Session wrappers attach `SAP` app-private tracking and trace sessions.

State and persistence: updates process-visible stdout progress, global path fields, `RWLOCK.lock_type`, trace session handles in `SAP`, and diagnostic `FAIL.pagedump.N` files. `set_core` mutates process rlimit state around unsafe dumps or expected failures.

Dependencies and integration: used broadly by `t.c`, `ops.c`, `verify.c`, `wts.c`, salvage, import, random cursor, and timestamp threads. It depends on `format.h`, WiredTiger internals, POSIX signals/rlimits, and test utility allocation/error helpers.

Risks and test signals: `track_write` assumes single-threaded callers. Diagnostic dump handlers are best-effort and only compiled under `HAVE_DIAGNOSTIC`. Wrapping sessions correctly is essential because trace routing and progress tags depend on `session->app_private`; leaks or stale app-private state can corrupt trace teardown.
