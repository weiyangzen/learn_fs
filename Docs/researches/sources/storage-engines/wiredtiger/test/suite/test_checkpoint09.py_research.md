# sources/storage-engines/wiredtiger/test/suite/test_checkpoint09.py

Purpose: verifies reconciliation clears obsolete time-window metadata for on-disk cells as oldest/stable timestamps advance.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `stat.conn.rec_time_window_start_ts`, helper `large_updates`, `check`, `evict_cursor`, `debug=(release_evict)`, and `wttest.prevent(["timestamp"])`.

Control flow: populate 1,000 rows, pin oldest/stable to 1, update all rows at timestamp 10, checkpoint and assert time-window start count equals 1,000. Evict, update every 10th row at timestamp 20, set oldest/stable 10/20, checkpoint and assert count increased by 100. Evict, update every 100th row at timestamp 30, set oldest/stable 20/30, checkpoint and assert count increased by 10.

State/persistence behavior: advancing oldest makes older time-window metadata obsolete, and checkpoints should rewrite cells accordingly. Eviction ensures pages are reconciled from disk state.

Dependencies/integration: timestamp manager, reconciliation stats, eviction debug cursor, row/column formats, and disaggregated page-delta config override.

Risks/test signals: exact stat counts make the test sensitive to reconciliation behavior changes.
