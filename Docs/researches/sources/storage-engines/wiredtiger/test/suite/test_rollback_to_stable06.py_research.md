# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable06.py

Purpose: validates that RTS removes all updates newer than a stable timestamp when a table only has unstable content. Scenarios cover column and integer row stores, prepared/non-prepared updates, in-memory/disk configurations, optional eviction pressure, and worker thread counts.

Important APIs/types/functions: `test_rollback_to_stable06` derives from `test_rollback_to_stable_base`. It uses `SimpleDataSet`, `conn.set_timestamp`, helper `large_updates` and `check`, optional eviction behavior from the scenario, explicit checkpointing, `conn.rollback_to_stable`, and `stat.conn` counters such as `txn_rts`, `txn_rts_keys_removed`, `txn_rts_upd_aborted`, and `txn_rts_hs_removed`.

Control flow: populates `table:rollback_to_stable06`, pins oldest/stable to 10, writes four full-table values at 20/30/40/50, checks each historical view, checkpoints for disk-backed runs, runs RTS with the selected thread count, and rechecks that reads at those timestamps return zero rows. It then checkpoints again and inspects RTS counters.

State and persistence behavior: the test specifically forces a state where there is no stable version of any key, so RTS should delete or abort all unstable updates. In-memory runs disable logging for the table and do not rely on on-disk checkpoint content. Prepared runs shift visible read timestamps by one because prepare/commit/durable timestamps are staged by the shared helper.

Dependencies and integration points: depends on the common RTS base helper for timestamped transactions and read validation, `wiredtiger.stat` for statistics, and the scenario generator. It integrates with history-store accounting because disk-backed updates may have history-store entries while in-memory updates do not.

Risks: the optional eviction scenario can change whether work is counted as keys removed versus updates aborted. The test mitigates this by checking combined counts where appropriate and by separately asserting no history-store removals.

Test signals: expects one RTS invocation, no key restoration, positive pages visited, nonnegative keys removed, no history-store removal, and `upd_aborted + keys_removed == nrows * 4` after final checkpoint.
