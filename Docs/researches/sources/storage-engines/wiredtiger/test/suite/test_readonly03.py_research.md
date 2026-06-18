# sources/storage-engines/wiredtiger/test/suite/test_readonly03.py

Purpose: confirms modifying cursor and session methods return unsupported errors after reopening an existing database in readonly mode.

Important APIs and types: `SimpleDataSet`, `cursor_ops` (`insert`, `remove`, `update`), `session_ops` (`alter`, `create`, `compact`, `drop`, `flush_tier`, `log_flush`, `log_printf`, `salvage`, `truncate`), `assertRaisesWithMessage`, and readonly connection configuration.

Control flow: the first open creates and populates a table. `reopen_conn` then uses readonly config. The test opens a cursor and checks each mutating cursor method raises `/Unsupported/`, then iterates through session-level mutating APIs and checks each also raises `/Unsupported/`.

State and persistence behavior: no state should be modified after readonly reopen; all attempted changes are blocked at API level.

Dependencies and integration points: connection readonly flag, cursor write APIs, session DDL/maintenance/log APIs, tier flush path, and error propagation.

Risks: adding new mutating session APIs would not be covered unless added to `session_ops`. The test intentionally uses a fixed list.

Test signals: every listed method raises `WiredTigerError` matching `/Unsupported/`.
