# sources/storage-engines/wiredtiger/test/suite/test_bug010.py

Purpose: regression test that checkpoints do not leave files marked clean when a checkpoint did not write all updates. It creates many tables, races a background checkpoint with updates, then verifies the next checkpoint sees a consistent value in every table.

Important APIs/types/functions: `wttest.WiredTigerTestCase`, `wtthread.checkpoint_thread`, `threading.Event`, `session.create`, `session.checkpoint`, and checkpoint cursors opened with `checkpoint=WiredTigerCheckpoint`. The class uses `conn_config = checkpoint_sync=false` to make checkpointing faster and `num_tables` scales under long-test mode.

Control flow: populate `num_tables` tables with key `a=0`; checkpoint; for iterations 1-9 start a checkpoint thread while updating every table to the next integer; stop/join the thread; take a foreground checkpoint; read every table from the checkpoint and assert the value matches the iteration.

State/persistence behavior: stresses dirty tracking across many btrees while checkpoints overlap with writes. The key invariant is that a later checkpoint cannot skip a file because an earlier concurrent checkpoint left it incorrectly clean.

Dependencies/integration: skipped for disaggregated hooks because checkpoint cursors are unsupported there. Integrates threading, checkpoint metadata, table handles, and checkpoint cursor visibility.

Risks/test signals: timing-sensitive by design; failures show as mismatched checkpoint values or checkpoint cursor errors rather than explicit internal stat checks.
