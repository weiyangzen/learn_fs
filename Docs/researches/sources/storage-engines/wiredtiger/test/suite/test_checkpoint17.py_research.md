# sources/storage-engines/wiredtiger/test/suite/test_checkpoint17.py

Purpose: validates that a checkpoint can still read needed history-store content when the history store is clean at the time a later checkpoint is taken. It covers named and unnamed checkpoints, row-store and column-store tables, and `precise_checkpoint` on/off.

Important APIs and types: `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `session.checkpoint`, checkpoint cursors with `checkpoint=` and `debug=(checkpoint_read_timestamp=...)`, and timestamp helpers from the test base.

Control flow: create an empty dataset, pin oldest/stable timestamps, write three timestamped full-table value generations, checkpoint at stable 30, write a disjoint key range at timestamp 40, checkpoint again, then open the later checkpoint at historical read timestamps 10, 20, and 30.

State and persistence behavior: the test intentionally makes the second checkpoint have no new history for the original key range, so history-store checkpoint retention is the persistence concern. It verifies old values remain reconstructable from the checkpoint even after the live tree has advanced.

Dependencies and integration points: depends on WiredTiger checkpoint cursor timestamp debug configuration and on history-store checkpoint matching. Skipped for disaggregated and tiered hooks because named checkpoint support or tiered behavior differs.

Risks: false failures can come from changes to checkpoint read timestamp semantics, history-store cleanup, or named checkpoint rules. The `zeros` argument is currently unused, so count-only absence checks rely on cursor iteration.

Test signals: success is all checkpoint cursor scans returning exactly `nrows` rows with the expected historical value for each timestamp and checkpoint precision scenario.
