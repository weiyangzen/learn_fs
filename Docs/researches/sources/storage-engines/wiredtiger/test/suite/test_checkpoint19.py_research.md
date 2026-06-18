# sources/storage-engines/wiredtiger/test/suite/test_checkpoint19.py

Purpose: timestamped companion to checkpoint cursor pinning tests. It verifies that checkpoint cursors opened at different checkpoint read timestamps keep access to the correct history-store checkpoint after a later checkpoint and history cleanup.

Important APIs and types: `WiredTigerTestCase`, `SimpleDataSet`, timestamped transactions, `session.open_cursor` with `checkpoint=WiredTigerCheckpoint,debug=(checkpoint_read_timestamp=...)`, and `make_scenarios`.

Control flow: create baseline data at timestamp 10, update odd keys at timestamps 20 and 30, checkpoint at stable 30, update even keys at timestamp 40, open three checkpoint cursors for read timestamps 10/20/30, advance stable to 40 and oldest to 35, checkpoint again, then scan all pinned cursors.

State and persistence behavior: advancing oldest past 30 makes older history eligible for cleanup. The test checks that already-open checkpoint cursors retain the historical version chain and matching history-store checkpoint despite later cleanup.

Dependencies and integration points: exercises timestamp visibility, history-store reconciliation, checkpoint cursor debug options, and precise/fuzzy checkpoint modes. Skipped for tiered and disaggregated hooks.

Risks: key parity is inferred from cursor scan count rather than parsing keys; changes in iteration order would break assumptions. History cleanup must actually rewrite involved history-store pages for the test to catch regressions.

Test signals: timestamp 10 sees all `value_a`; timestamp 20 sees odd `value_b` and even `value_a`; timestamp 30 sees odd `value_c` and even `value_a`.
