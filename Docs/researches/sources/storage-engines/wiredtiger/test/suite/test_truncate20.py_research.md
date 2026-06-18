# sources/storage-engines/wiredtiger/test/suite/test_truncate20.py

## Purpose
`test_truncate20.py` is a long oplog-like truncate workload. It verifies that repeated range truncation of old records, append of new records, eviction, and checkpoint cleanup do not let the on-disk table file grow without bound.

## Important APIs, Types, and Functions
The file defines `test_truncate20(test_cc_base)`, scenarios for column, integer row, and string row tables, and helpers `append_rows`, `do_truncate`, `evict_cursor`, and `test_truncate`. It uses `SimpleDataSet`, `session.truncate`, debug eviction cursors, connection statistics, `stat.conn.rec_page_delete_fast`, and `test_cc_base.wait_for_cc_to_run`.

## Control Flow
The test populates one million rows, evicts pages with `debug=(release_evict)`, then loops 49 times. Each iteration opens a long transaction to hold visibility, truncates 10,000 starting rows, checks fast-delete stats, appends replacement rows, evicts again, waits for checkpoint cleanup, and checks `oplog.wt` size.

## State and Persistence Behavior
The persisted state is `table:oplog` plus its `oplog.wt` file under logging. The long reader keeps deletes not globally visible while checkpoints and cleanup must still reclaim enough obsolete disk state.

## Dependencies and Integration Points
Depends on `wttest`, `test_cc01.test_cc_base`, `wtdataset.SimpleDataSet`, `wiredtiger.stat`, `os.path.getsize`, and `wtscenario`.

## Risks and Edge Cases
This is resource-heavy and marked longtest. It is sensitive to cache eviction, page layout, checkpoint cleanup timing, and a hard 600 MB disk-size threshold.

## Test Signals
Signals are positive fast-delete page statistics and repeated/final `oplog.wt` size assertions below 600 MB.
