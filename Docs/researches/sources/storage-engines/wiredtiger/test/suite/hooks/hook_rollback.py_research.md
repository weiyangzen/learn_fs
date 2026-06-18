<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py

Purpose: Fault-injection hook that randomly raises `WiredTigerRollbackError` from cursor operations inside transactions to test suite-level rollback retry and cleanup behavior.

Important APIs and types: Notification hooks `session_begin_transaction_notify`, `session_end_transaction_notify`, `session_open_cursor_notify`, `cursor_notify_for_rollback`, and `RollbackHookCreator`. The module also replaces `wiredtiger.Cursor.session` with a Python property returning the original session wrapper.

Control flow: Begin/commit/rollback notifications maintain `session.in_transaction`. Open-cursor notification records the creating session on the cursor. Cursor operation notifications for insert, modify, search, search_near, and update call `cursor_notify_for_rollback`; if the session is in a transaction and `do_retry()` matches the configured random rate, the hook prints a retry marker and raises `WiredTigerRollbackError`.

State and persistence behavior: Runtime state includes per-session `in_transaction`, per-cursor `_session_value`, a random generator, and an integer modulus derived from the fail rate. It does not intentionally persist data, but injected rollbacks force test retries and cleanup paths.

Dependencies and integration points: Integrates with `WiredTigerTestCase._callTestMethod`, which catches `WiredTigerRollbackError`, tears down, and restarts tests up to `rollbacks_allowed`.

Risks: Fail-rate `1.0` yields modulus one and always injects during eligible operations, while very small rates produce large moduli. The hook globally changes `Cursor.session`, which can affect other code in the process. Printed retry markers must be cleaned up by retry output handling.

Test signals: Expected rollback retries, cleaned stdout between retries, and final failures only after retry limits are exhausted validate the suite retry machinery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py -->
