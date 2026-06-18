# sources/storage-engines/wiredtiger/test/suite/helpers/checkpoint_util.py

Purpose: mixin/base class with checkpoint-specific helpers for Python suite tests.

Important APIs and control flow: `checkpoint_util` extends `wttest.WiredTigerTestCase`. `wait_for_checkpoint_start()` opens a `statistics:` cursor, polls `stat.conn.checkpoint_state`, and waits until it becomes nonzero, sleeping between attempts and asserting before a timeout expires.

State and persistence behavior: no persistent state beyond polling statistics. Uses the provided session or `self.session`.

Dependencies and integration points: depends on `wttest.open_cursor`, WiredTiger statistics cursors, and `wiredtiger.stat.conn.checkpoint_state`. Used by tests that need to coordinate with a running checkpoint.

Risks: polling interval and timeout balance flake detection against slow environments. If statistics are disabled or checkpoint state semantics change, the helper can false-fail.

Test signals: tests using the helper should fail quickly with a clear timeout if checkpoints never start.
