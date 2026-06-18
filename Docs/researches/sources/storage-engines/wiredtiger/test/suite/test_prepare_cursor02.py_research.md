# sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor02.py

Purpose: verifies that a reader encountering a single prepared insert in an otherwise empty table receives repeated prepare conflicts for `search`, `next`, and `prev`, rather than silently skipping or corrupting cursor position.

Important APIs and types: `WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `wiredtiger.WiredTigerError`, session `prepare_transaction`, cursor `search`, `next`, `prev`, and scenario coverage for row-store integer keys and column-store recno keys.

Control flow: the main session inserts key 1 and prepares at timestamp 100. A second session starts a transaction and opens a cursor on the same URI. It sets key 1, asserts `search` raises a prepare conflict, then calls `next` twice and expects both to raise. It repeats the pattern for `prev`. The prepared writer is rolled back at the end.

State and persistence behavior: no checkpoint or recovery is involved; the durable state remains empty after rollback. The key state is an in-memory prepared update visible enough to block conflicting cursor operations.

Dependencies and integration points: integrates prepare conflict handling with bidirectional cursor navigation and both row/column key formats through `wtscenario`.

Risks: repeated calls after an error can expose cursor reset bugs. The test relies on the default session configuration for the reader; changes to isolation defaults could affect conflict timing.

Test signals: every read attempt against the prepared key raises `WiredTigerError`; no operation returns a found key or `WT_NOTFOUND` while the prepare is unresolved.
