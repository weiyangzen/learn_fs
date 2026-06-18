# sources/storage-engines/wiredtiger/test/suite/test_truncate27.py

## Purpose
`test_truncate27.py` verifies recovery after timestamped fast truncate, later stable timestamp movement, further updates, checkpoint, and crash restart.

## Important APIs, Types, and Functions
The test defines `evict_cursor`, `get_fast_truncated_pages`, and `test_truncate27`. It uses release-evict debug cursors, column-store table format, timestamped row inserts, `stat.conn.rec_page_delete_fast`, `session.truncate`, checkpoints, and `simulate_crash_restart`.

## Control Flow
It creates and populates 10,000 timestamped rows, advances stable timestamp and checkpoints, evicts pages, checkpoints again, truncates from key 1 to the end at the next timestamp, asserts fast-delete stats increased, advances stable, writes one new row after the truncated range, checkpoints, and simulates crash restart.

## State and Persistence Behavior
The test persists a column-store file with timestamped updates and fast-delete page metadata. Recovery must replay the truncate and later insert without losing consistency.

## Dependencies and Integration Points
Depends on the helper crash restart path, WiredTiger statistics, timestamp APIs, and debug eviction support.

## Risks and Edge Cases
The important edge is fast-delete metadata crossing a crash boundary after timestamps and checkpoints have moved. A missed recovery path may leave deleted rows visible or corrupt the new append.

## Test Signals
The direct signal is `fast_truncates_pages > 0`; successful crash restart without assertion failure completes the recovery check.
