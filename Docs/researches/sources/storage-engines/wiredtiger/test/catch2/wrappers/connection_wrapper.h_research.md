# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h

## sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h

Purpose: Header for the real WiredTiger `connection_wrapper` test utility.

Important API: constructor takes DB home and optional config defaulting to `create`; destructor closes and cleans up; `create_session` returns a `WT_SESSION_IMPL *`; accessors return `WT_CONNECTION_IMPL *` and `WT_CONNECTION *`; `clear_do_cleanup` preserves the home directory.

Control flow/state: the class owns `_conn_impl`, `_conn`, `_db_home`, `_cfg_str`, and `_do_cleanup`. Header comments explain returned sessions are owned by the connection and need not be freed by callers.

Dependencies/integration: includes `wt_internal.h` and a Windows shim when needed. It is used by many tests requiring full WiredTiger, including sub-level error, reconciliation, and truncate integration tests. Risks include exposing internal pointers and tests relying on connection lifetime. Test signals are indirect through real connection/session operations.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.h -->
