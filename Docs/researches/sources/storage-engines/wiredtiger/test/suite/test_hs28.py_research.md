# sources/storage-engines/wiredtiger/test/suite/test_hs28.py

Purpose: ensures reconciliation inserts full updates into the history store, rather than reverse modifies, when a modify follows a squashed on-page value. This protects reconstruction correctness for modify chains.

Important APIs and functions: `test_hs28` extends `WiredTigerTestCase`; scenarios cover column-store recno and integer row-store. `conn_config` enables all statistics and JSON stats logging. The test uses `wiredtiger.Modify`, cursor `modify`, `session.checkpoint`, and statistics `cache_hs_insert_full_update` and `cache_hs_insert_reverse_modify`.

Control flow: the test creates a table, inserts a full value at timestamp 2, applies a modify at timestamp 5, then commits multiple updates on the same key at timestamp 10. A checkpoint moves older versions to the history store. It reads connection statistics and asserts the expected insert mode.

State and persistence behavior: checkpoint reconciliation is the persistence transition. The previous on-page value has been squashed, so using reverse modify would not leave enough information to reconstruct old values safely.

Dependencies and integration points: uses the Python WiredTiger API `Modify` object, history-store insert statistics, and reconciliation policy for update chains.

Risks and edge cases: this is a statistic-based behavioral assertion; if implementation changes update accounting while preserving correctness, the expected counts may require adjustment. It does not read historical values directly.

Test signals: after checkpoint, `cache_hs_insert_full_update == 2` and `cache_hs_insert_reverse_modify == 0`.
