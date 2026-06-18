# sources/storage-engines/wiredtiger/test/thread/t.c

## Purpose

`t.c` is the main program for the WiredTiger thread stress test. It parses options, creates a test home, opens a connection, runs concurrent readers/writers, dumps stats, and shuts down cleanly.

## Important APIs, Types, and Functions

It defines global options/connection state plus `main`, `wt_connect`, `wt_shutdown`, `shutdown`, `handle_error`, `handle_message`, `onint`, and `usage`. It uses `__wt_getopt`, `testutil_work_dir_from_path`, `testutil_recreate_dir`, `wiredtiger_open`, `rw_start`, and `stats`.

## Control Flow

`main` initializes defaults, parses flags for config, multiple files, keys, logging, operation count, reader/writer counts, runs, per-operation sessions, file type, and varying ops. For each run it removes previous state, opens WiredTiger with statistics logging and event handler, starts read/write workload, writes stats, checkpoints and closes the connection.

## State and Persistence Behavior

State includes global configuration, the work directory, optional log file, connection statistics log on close, table data from workload, and cleanup on SIGINT or next run.

## Dependencies and Integration Points

Depends on `thread.h`, test utility work-directory/file helpers, event-handler callbacks, `rw_start`, `stats`, and WiredTiger connection/session APIs.

## Risks and Edge Cases

`vary_nops` is only allowed with multiple files. Signal cleanup removes the work directory. Event messages go to either the configured log file or stdout.

## Test Signals

Signals are process/run banners, successful workload completion, stats output, checkpoint on shutdown, and zero exit.
