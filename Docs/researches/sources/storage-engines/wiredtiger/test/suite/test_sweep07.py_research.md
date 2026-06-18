# sources/storage-engines/wiredtiger/test/suite/test_sweep07.py

## Purpose
`test_sweep07.py` is a regression test for WT-15647. It verifies that a table handle can be swept after the last cursor and session references are released.

## Important APIs, Types, and Functions
The file defines `test_sweep07`, a `WiredTigerTestCase` using `file_manager=(close_scan_interval=1,close_idle_time=1,close_handle_minimum=1)` to make sweep activity observable quickly. It uses `wiredtiger.stat.conn.dh_sweep_remove` to detect actual handle removal.

## Control Flow
`test_sweep_with_cursor` creates a table, opens and closes an initial cursor after writing one key, then sleeps to allow unrelated history-store cleanup. It records the initial sweep-remove statistic, checkpoints, opens a second session and cursor, reads one record, closes them, closes the original session to release the final reference, sleeps again, then reopens a session and asserts the remove statistic increased.

## State and Persistence Behavior
The table has one persisted key and a checkpoint so the dhandle is eligible for normal lifecycle management. The important state transition is from referenced handle to unreferenced handle after session close.

## Dependencies and Integration Points
The test depends on `time.sleep`, WiredTiger session/cursor/checkpoint/statistics APIs, and file-manager sweep timing configuration.

## Risks and Test Signals
Timing is the main fragility: it relies on short sweep intervals and sleeps. The signal is `remove2 > remove1`, proving the sweep server removed at least one eligible handle after cursor/session closure.
