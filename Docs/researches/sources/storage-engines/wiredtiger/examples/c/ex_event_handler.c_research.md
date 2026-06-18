# sources/storage-engines/wiredtiger/examples/c/ex_event_handler.c

Purpose: demonstrates custom WiredTiger event handling for errors and messages.

Important APIs and control flow: `CUSTOM_EVENT_HANDLER` embeds `WT_EVENT_HANDLER` first and adds an `app_id`. `handle_wiredtiger_error` casts back to the custom type, prints app/session/error/message context, and exits on `WT_PANIC`. `handle_wiredtiger_message` prints app/session/message context. `config_event_handler` initializes callback pointers, leaves unsupported callbacks as `NULL`, opens WiredTiger with the handler, deliberately calls `open_session` with invalid isolation to trigger error handling, and closes the connection.

State and persistence: creates a WT_HOME connection but the main purpose is callback behavior; no table data is persisted.

Dependencies and integration: uses the public `WT_EVENT_HANDLER` callback ABI and `test_util.h`.

Risks: fatal error handling calls `exit(1)`, which is acceptable for example code but not a reusable library pattern. The deliberate invalid call ignores its return value because the handler output is the test signal.

Test signals: run output should contain the expected error message bracketed by the example's `expect` and `end` lines, and connection close should succeed.
