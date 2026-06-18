# sources/storage-engines/wiredtiger/test/suite/test_debug_info.py

Purpose: smoke tests the undocumented `WT_CONNECTION::debug_info` entry points for handles, sessions, cursors, special cursors, and backup state.

Important APIs and control flow: `test_debug` wraps `conn.debug_info()` calls with `expectedStdoutPattern`. `conn_cursors` creates a file, inserts keys, positions a cursor by reading key 50, calls `debug_info('cursors')`, and expects positioned-cursor output. `conn_cursors_special` opens `backup:`, `log:`, `metadata:`, and `statistics:` cursors and checks that their URIs appear.

State and persistence: connection logging and fast statistics are enabled. The test creates a file and an incremental backup cursor, but validates stdout diagnostics rather than persisted data.

Dependencies and integration: relies on `wttest` stdout pattern capture and special WiredTiger cursor URI support.

Risks and test signals: output strings such as `Data handle dump`, `Active`, `POSITIONED`, and backup ID `ID1` are brittle but useful integration signals for diagnostic formatting regressions.
