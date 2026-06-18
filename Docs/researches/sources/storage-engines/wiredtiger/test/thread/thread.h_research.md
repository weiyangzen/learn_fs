# sources/storage-engines/wiredtiger/test/thread/thread.h

## Purpose

`thread.h` is the shared header for the thread stress executable. It centralizes file-name constants, global option declarations, file type enum, and cross-file function prototypes.

## Important APIs, Types, and Functions

It defines `FNAME`, `FNAME_STAT`, enum `__ftype { ROW, VAR }`, extern globals `conn`, `ftype`, `log_print`, `multiple_files`, `nkeys`, `max_nops`, `vary_nops`, `session_per_op`, and prototypes `load`, `rw_start`, and `stats`.

## Control Flow

There is no runtime flow in the header; it provides the compile-time contract among `t.c`, `file.c`, `rw.c`, and `stats.c`.

## State and Persistence Behavior

The declared globals carry process-wide runtime state. Constants name persistent WiredTiger files and the stats output file.

## Dependencies and Integration Points

Depends on `test_util.h` and `<signal.h>`, and is included by all thread-test implementation files.

## Risks and Edge Cases

Global mutable state keeps the small harness simple but couples all implementation files and makes concurrent multiple harness instances inside one process impossible.

## Test Signals

Compile-time signals are successful cross-file linkage and consistent option state across the stress harness.
