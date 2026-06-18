# sources/storage-engines/wiredtiger/test/suite/test_truncate21.py

## Purpose
`test_truncate21.py` tests logging and recovery when a truncate range is repeated and may have no remaining work, including an overlapping insert into the previously truncated range.

## Important APIs, Types, and Functions
The file defines `test_truncate21(wttest.WiredTigerTestCase)`, `trunc_range`, and `test_truncate21`. It uses a small cache, logging, integer row-store keys, `session.truncate`, `session.log_flush`, `copy_wiredtiger_home`, `wiredtiger_open`, and `WT_NOTFOUND`.

## Control Flow
The test creates `table:trunc_row`, inserts 999 committed records one transaction at a time, checkpoints, truncates the middle range, then opens a second session. The first session repeats the truncate while the second inserts the middle key and commits. After the truncate commits, the home is copied, reopened, and the inserted key is searched.

## State and Persistence Behavior
The core state is a logged table and copied home directory `newdir`. Recovery must replay a repeated no-op truncate correctly and must not resurrect or preserve the overlapped key after the truncate transaction commits.

## Dependencies and Integration Points
Integrates WiredTiger Python API transaction/truncate logging with helper-based home copying and restart recovery.

## Risks and Edge Cases
The edge case is a truncate range that already has tombstones while another committed transaction inserts inside that range. Ordering in the log must remain correct.

## Test Signals
After recovery, searching `insert_key` returns `WT_NOTFOUND`.
