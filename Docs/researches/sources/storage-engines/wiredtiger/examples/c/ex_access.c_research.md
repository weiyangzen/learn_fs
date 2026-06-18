# sources/storage-engines/wiredtiger/examples/c/ex_access.c

Purpose: minimal C walkthrough for creating and reading a string-key/string-value table.

Important APIs and control flow: `main` obtains a home directory via `example_setup`, then calls `access_example`. The example opens a connection with `wiredtiger_open(home, NULL, "create,statistics=(all)", &conn)`, opens a session, creates `table:access` with `key_format=S,value_format=S`, opens a cursor, inserts `key1/value1`, resets the cursor, scans with `next`, reads with `get_key`/`get_value`, and closes the connection.

State and persistence: persists one table and one record under the configured WT_HOME. Cursor state is reset before scanning, and connection close implicitly closes session/cursor handles.

Dependencies and integration: depends on `test_util.h` helpers (`example_setup`, `error_check`, `scan_end_check`) and the public WiredTiger C API. Snippet markers feed documentation extraction.

Risks: intentionally simple error behavior exits through `error_check`; it is not an example of recovery from failures. The table name overlaps with statistics examples but per-test home isolation prevents conflicts.

Test signals: target execution should print `Got record: key1 : value1` and terminate after `WT_NOTFOUND`.
