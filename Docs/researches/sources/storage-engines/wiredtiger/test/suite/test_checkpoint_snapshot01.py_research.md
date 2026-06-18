# sources/storage-engines/wiredtiger/test/suite/test_checkpoint_snapshot01.py

Purpose: verifies checkpoint metadata can be saved while multiple sessions hold active snapshots with uncommitted inserts.

Important APIs and types: `copy_wiredtiger_home`, `SimpleDataSet`, multiple sessions/cursors, `begin_transaction`, and `session.checkpoint`.

Control flow: create a table, open five sessions, each begins a transaction and inserts a disjoint range beyond the initial rows without committing, run checkpoint in another session, copy the home directory to simulate crash material, then open the copied home.

State and persistence behavior: checkpoint must persist consistent snapshot metadata despite active uncommitted transactions. The copied home must be openable after the checkpoint.

Dependencies and integration points: tests metadata checkpointing and connection setup helpers. Tagged as `checkpoint:metadata`.

Risks: it does not assert table contents after reopening, so the main signal is absence of crash/open failure. The value format uses raw bytes (`u`) in both column and row-string scenarios.

Test signals: the copied checkpointed home opens successfully after uncommitted transactional activity.
