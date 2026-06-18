# sources/storage-engines/wiredtiger/test/suite/test_durable_rollback_to_stable.py

Purpose: validates durable timestamp visibility and rollback-to-stable behavior for prepared transactions.

Important APIs and control flow: scenarios cover file/table simple row formats. The test populates 50 records, checkpoints at stable timestamp 100, prepares and commits value 111 at commit 200 durable 220, verifies reads at timestamp 150 and 220, then prepares value 222 with commit 240 but durable 300 while stable is 250. After checkpoint, latest reads see 222, then `conn.rollback_to_stable()` must restore 111.

State and persistence: state includes prepare, commit, durable timestamps, stable timestamp, checkpoint, and rollback-to-stable. Utility `wt verify -s` checks flushed state afterward.

Dependencies and integration: uses `SimpleDataSet`, `make_scenarios`, `suite_subprocess`, timestamp APIs, prepared transactions, and `rollback_to_stable`.

Risks and test signals: catches durable timestamp ordering mistakes where updates visible before rollback are incorrectly retained or discarded after RTS.
