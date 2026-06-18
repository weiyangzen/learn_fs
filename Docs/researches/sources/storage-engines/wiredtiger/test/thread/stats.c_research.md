# sources/storage-engines/wiredtiger/test/thread/stats.c

## Purpose

`stats.c` dumps connection and file statistics for the thread stress executable after each run.

## Important APIs, Types, and Functions

It defines `stats(void)`, opens `statistics:` and optionally `statistics:file:wt.000`, and writes `desc=pval` pairs to `__stats`.

## Control Flow

The function opens a session, creates the stats output file, scans the connection statistics cursor until `WT_NOTFOUND`, closes it, then if not in multiple-file mode scans file statistics for `FNAME` index 0 and closes the session/file.

## State and Persistence Behavior

The persistent output is `__stats`, overwritten with current statistic descriptions and printable values. It reads live statistics from the WiredTiger connection.

## Dependencies and Integration Points

Depends on `thread.h`, global `conn` and `multiple_files`, WiredTiger statistics cursors, and test utility error handling.

## Risks and Edge Cases

In multiple-file mode, it closes the output file but does not close the session in the visible control path, which may be a resource leak. It only emits file stats for single-file runs.

## Test Signals

Signals are successful cursor scans and a populated `__stats` file.
