# sources/storage-engines/wiredtiger/examples/c/ex_hello.c

Purpose: smallest canonical C example for opening a WiredTiger database and session.

Important APIs and control flow: `main` calls `example_setup`, opens a connection with `wiredtiger_open(home, NULL, "create", &conn)`, opens a session with `conn->open_session`, does no table work, and closes the connection. The close call implicitly closes the open session.

State and persistence: creates a WT_HOME database directory and metadata files. No user table data is created.

Dependencies and integration: depends on `test_util.h` for setup/error handling and the public WiredTiger C API.

Risks: intentionally omits cleanup, explicit session close, and any transactional or schema behavior. It should not be treated as an operational template beyond connection/session lifecycle basics.

Test signals: successful open/session/close proves basic library linkage and runtime initialization under the example harness.
