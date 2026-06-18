# sources/storage-engines/wiredtiger/test/suite/test_drop03.py

Purpose: tests dropping a table around an active transaction and dirty content, with explicit force true/false semantics.

Important APIs and control flow: writes initial values, verifies them, starts a transaction that overwrites values, then `session.drop(uri, "force=false")` must raise busy. The active transaction still sees new values; commit must fail with "transaction requires rollback"; after rollback, old values are visible. A later non-force drop of dirty table still fails, while `force=true` succeeds.

State and persistence: table content transitions between committed base values, uncommitted transactional values, rollback, dirty table state, and final metadata removal.

Dependencies and integration: uses `confirm_nonempty`, `confirm_does_not_exist`, `raisesBusy`, and `wiredtiger.WiredTigerError`.

Risks and test signals: covers important user-visible drop semantics: active transaction protection, rollback requirements, and missing-table force behavior.
