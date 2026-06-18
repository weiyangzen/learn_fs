# sources/storage-engines/wiredtiger/test/syscall/wt2336_base/main.c

## Purpose

`wt2336_base/main.c` is a small syscall-test executable for WT-2336-style file-operation tracing. It performs a predictable sequence of WiredTiger API calls with marker output to stderr.

## Important APIs, Types, and Functions

It defines `fail(int ret)` and `main`. `main` calls `wiredtiger_open`, `WT_CONNECTION.open_session`, `WT_SESSION.create`, `WT_SESSION.drop`, and `WT_CONNECTION.close`. It uses `SEPARATOR` marker strings.

## Control Flow

The program prints marker lines before each major API operation, sleeps briefly to improve trace separation, opens a database with statistics logging, creates and drops `table:hello`, closes the connection, and exits. Any nonzero WiredTiger return calls `fail`.

## State and Persistence Behavior

It creates a WiredTiger home in the current directory, creates then drops a table, and leaves normal WiredTiger metadata/log/statistics artifacts for the syscall trace.

## Dependencies and Integration Points

Depends on `wt_internal.h`, WiredTiger C API, POSIX `usleep`, and the syscall runner matching stderr markers with expected syscalls.

## Risks and Edge Cases

The TODO comments indicate sparse in-source documentation. Trace timing and marker flushing are important; missing flushes could make comparisons harder.

## Test Signals

Signals are stderr separators interleaved with traced open/create/drop/close syscalls and zero process exit.
