# sources/storage-engines/wiredtiger/test/suite/test_truncate29.py

## Purpose
`test_truncate29.py` checks that fast truncate can operate correctly on variable-sized random byte-like string values and reports fast-delete page statistics.

## Important APIs, Types, and Functions
The class defines `generate_random_string`, `get_fast_truncated_pages`, and `test_truncate29`. It uses `random`, `string`, `SimpleDataSet`, row/column scenarios, `session.truncate`, `session.checkpoint`, and `stat.conn.rec_page_delete_fast`.

## Control Flow
The test populates a file-backed table with 10,000 rows of random string values, checkpoints to make pages durable, records the current fast-delete statistic, truncates a key range using positioned cursors, checkpoints again, and compares the statistic after truncation.

## State and Persistence Behavior
The persisted state is `file:test_truncate29` with random values large enough to exercise page-level storage behavior. Fast-delete metadata should persist through checkpoint rather than expanding into per-key deletes.

## Dependencies and Integration Points
Depends on Python random/string generation, `SimpleDataSet` key handling, and WiredTiger fast-delete statistics.

## Risks and Edge Cases
Random values can vary page packing and may expose assumptions about fixed-size values. The test also risks flakiness if the generated data does not produce pages eligible for fast truncate.

## Test Signals
The main signal is an increase in `rec_page_delete_fast` after checkpointing the truncated range.
