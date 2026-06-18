# sources/storage-engines/wiredtiger/test/suite/test_checkpoint03.py

Purpose: verifies checkpoints write older updates to the history store and that the latest update remains readable after reopen.

Important APIs/types/functions: `suite_subprocess`, `stat.conn.cache_write_hs`, `make_scenarios`, `session.checkpoint`, timestamp APIs, `setUpConnectionOpen`, and `setUpSessionOpen`.

Control flow: create a table, commit three updates to key 1 at timestamps 2, 3, and 4, set oldest/stable to 1/4, checkpoint, assert `cache_write_hs >= 1`, commit another update at timestamp 5, set stable to 5, checkpoint again, assert `cache_write_hs >= 2`, close/reopen, and verify key 1 reads value 4.

State/persistence behavior: checkpoint reconciliation should place older versions in the HS and latest stable value in the data file. Reopen validates persisted latest state.

Dependencies/integration: history store write statistics, timestamped updates, checkpoint precision modes, and row/column formats.

Risks/test signals: HS stat is coarse, so assertions are lower bounds. Failure can indicate no HS write or incorrect latest persisted value.
