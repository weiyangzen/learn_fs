# sources/storage-engines/wiredtiger/examples/c/ex_verbose.c

Purpose: demonstrates verbose message configuration and message callbacks.

Important APIs and control flow: defines `handle_wiredtiger_message`, which prints the session pointer and message. `config_verbose` initializes a `WT_EVENT_HANDLER` with only `handle_message`, opens WiredTiger with `verbose=[api:1,all:0,version,write:2]`, then makes API calls (open session, create table, open cursor, insert row, close cursor) to trigger verbose messages before closing.

State and persistence: creates `table:verbose` and inserts `foo/bar`. Verbose output is emitted through the callback, not persisted by this example.

Dependencies and integration: depends on verbose category syntax and the `WT_EVENT_HANDLER` ABI. Uses `test_util.h`.

Risks: verbose category names and levels are version-sensitive. Message volume is controlled by config and may change as APIs emit different diagnostics.

Test signals: output should include verbose messages between the example's `expect` and `end` markers, and all API calls should succeed.
