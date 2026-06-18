# sources/storage-engines/wiredtiger/examples/c/ex_log.c

Purpose: demonstrates logging, log cursors, application log records, replaying row-put operations into a second database, and searching logs by LSN.

Important APIs and control flow: `main` creates two homes, opens `home1` with logging and removal disabled, creates `table:logtest`, inserts 10 auto-commit records and 5 transaction records, writes an application log message, closes/reopens, then calls `simple_walk_log` and `walk_log`. `simple_walk_log` opens `log:`, prints key/value fields, and enforces a minimum record count. `walk_log` opens a second logged copy, scans log records, tracks a saved LSN, replays `WT_LOGOP_ROW_PUT` records for non-metadata file IDs through a raw cursor into the copy under transactions, compares tables, then resets/searches the log cursor to the saved LSN and scans from there.

State and persistence: creates two database homes and logged table state. Log files persist because `remove=false`.

Dependencies and integration: requires POSIX target gating, `test_util_system`, log cursor value layout, raw table cursor behavior, and the `WT_LOGREC_*`/`WT_LOGOP_*` constants.

Risks: replay logic only handles row-put records and intentionally skips metadata. It assumes log record ordering and transaction boundaries via `opcount == 0`. It is not a general log recovery implementation.

Test signals: log walk count must meet `count_min`; replayed copy must compare identical to the original; LSN search must return the saved file/offset.
