# sources/storage-engines/wiredtiger/test/suite/test_drop_create.py

Purpose: tests repeated drop/create cycles and session table-cache invalidation when a table name is reused with different schema.

Important APIs and control flow: `test_drop_create` closes the default session, opens a new one, repeatedly force-drops and creates `table:test` with string schema, drops it, closes/reopens sessions, and creates again. `test_drop_create2` uses two sessions: one creates and drops the table, the other opens cursors before and after recreation with a different value format.

State and persistence: metadata for `table:test` is removed and recreated. The important state is per-session table cache awareness after drop and schema change.

Dependencies and integration: uses raw WiredTiger session APIs through `self.conn.open_session()`, `create`, `drop`, `open_cursor`, and explicit session close.

Risks and test signals: failures indicate stale cached schema or incorrect table name reuse across sessions.
