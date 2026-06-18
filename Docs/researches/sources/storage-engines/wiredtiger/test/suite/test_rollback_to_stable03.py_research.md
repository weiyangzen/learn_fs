# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable03.py

Purpose: checks rollback-to-stable clears history-store updates from reconciled pages and reports btree applied/skipped counters correctly across repeated RTS calls.

Important APIs and types: `WiredTigerCursor`, `statistic_uri`, `test_rollback_to_stable_base`, `large_updates`, `check`, `conn.rollback_to_stable`, and RTS counters such as `txn_rts_hs_removed`, `txn_rts_btrees_applied`, and `txn_rts_btrees_skipped`.

Control flow: it writes three generations at timestamps 10, 20, and 30, sets stable to 30 for prepared or 20 otherwise, checkpoints when not in-memory, runs RTS, verifies values B and A at timestamps 20 and 10, and checks stats. It then runs RTS a second time and verifies btree applied/skipped behavior differs for in-memory and non-in-memory modes.

State and persistence behavior: value C should be rolled back to value B at stable, with older value A still available. Non-in-memory RTS can clear modified flags through checkpoint, causing a second RTS to skip clean btrees; in-memory keeps modified flags.

Dependencies and integration points: history store cleanup, RTS btree scanning, checkpoint side effects, in-memory mode, and prepared update semantics.

Risks: applied/skipped accounting is nuanced and can be affected by eviction modifying the tree before the second RTS.

Test signals: data checks pass, first RTS has one applied btree and zero skipped, and second RTS counters match mode-specific expectations.
