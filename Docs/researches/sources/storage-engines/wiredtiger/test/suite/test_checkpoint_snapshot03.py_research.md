# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot03.py

Purpose: verifies rollback-to-stable can skip unnecessary pages when a table contains more than the checkpoint snapshot, avoiding needless update aborts or restores.

Important APIs and types: `simulate_crash_restart`, `SimpleDataSet`, RTS statistics (`txn_rts_inconsistent_ckpt`, `txn_rts_keys_removed`, `txn_rts_keys_restored`, `txn_rts_tree_walk_skip_pages`, `txn_rts_upd_aborted`), and `make_scenarios`.

Control flow: hold an uncommitted insert beyond the main range, bulk-update 500,000 rows, checkpoint, rollback and reopen; repeat with a new uncommitted insert plus one committed update, checkpoint, rollback, crash/restart, then inspect RTS stats.

State and persistence behavior: restart recovery should identify inconsistent checkpoint state but skip pages that do not require rollback. No updates should be aborted or restored for the stable main content.

Dependencies and integration points: row-string and column scenarios, cache/statistics configuration, and crash simulation. Disaggregated is skipped because RTS behavior is not expected there.

Risks: large dataset and cache size make it heavier. Assertions around inconsistent checkpoint and skipped pages are bypassed for disaggregated hook even though class is skipped for that hook.

Test signals: `txn_rts_upd_aborted == 0`, `txn_rts_keys_restored == 0`, inconsistent checkpoint and page-skip stats are positive in normal runs.
