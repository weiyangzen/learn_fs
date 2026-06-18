# sources/storage-engines/wiredtiger/examples/c/ex_thread.c

Purpose: demonstrates using one `WT_CONNECTION` from multiple threads, with one session/cursor per thread.

Important APIs and control flow: `main` creates `table:access`, inserts one row, closes the setup session, then starts `NUM_THREADS` worker threads using `__wt_thread_create`. Each `scan_thread` opens its own session and cursor on the shared connection and scans all records, printing each key/value. The main thread joins all workers with `__wt_thread_join` and closes the connection.

State and persistence: persists a single row. Thread state is isolated by per-thread sessions and cursors; the connection is shared.

Dependencies and integration: depends on WiredTiger internal test thread wrappers (`wt_thread_t`, `__wt_thread_create`, `__wt_thread_join`) via `test_util.h`, plus public session/cursor APIs.

Risks: worker sessions/cursors are not explicitly closed before thread return, relying on connection close. The workload is read-only after setup and does not demonstrate concurrent writes or transaction conflicts.

Test signals: all threads should print the inserted row and terminate without errors other than expected scan `WT_NOTFOUND`.
