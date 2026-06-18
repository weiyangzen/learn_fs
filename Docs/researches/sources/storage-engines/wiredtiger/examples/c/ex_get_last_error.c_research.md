# sources/storage-engines/wiredtiger/examples/c/ex_get_last_error.c

Purpose: demonstrates the `WT_SESSION.get_last_error` API for retrieving detailed session error state.

Important APIs and control flow: `main` sets up WT_HOME, opens a connection and session, prepares `err`, `sub_level_err`, and `err_msg`, calls `session->get_last_error(session, &err, &sub_level_err, &err_msg)`, prints all three returned values, and closes the connection.

State and persistence: no table state is created. The session-level last-error fields are read immediately after opening the session, so the example primarily shows API shape rather than a populated failure case.

Dependencies and integration: uses `test_util.h` and public connection/session APIs. It integrates with documentation that explains verbose session error information.

Risks: because no failing session operation precedes `get_last_error`, output may represent a no-error/default state. Consumers copying the pattern should call it after an API failure on the same session.

Test signals: successful execution and stable printed fields validate ABI compatibility. A stronger test would trigger a known session error and assert the primary and sub-level error codes.
