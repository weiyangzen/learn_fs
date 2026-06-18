# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h

## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h

Purpose: Header for mock session support used across Catch2 internal tests.

Important declarations: free functions `handle_wiredtiger_error` and `handle_wiredtiger_message`, `event_handler_wrap`, and class `mock_session` with accessors for `WT_SESSION_IMPL` and `mock_connection`, callback message storage, static builder, block-manager setup helpers, and private owned pointers.

Control flow/state: the header defines the relationship between the WT event handler and the C++ mock through `event_handler_wrap::ms`. The class owns the session pointer and shared connection.

Dependencies/integration: includes `mock_connection.h` and `wt_internal.h`; used by semaphore, verify, truncate, and many misc tests. Risks are public exposure of mutable internals and message-list assumptions. Test signals are indirect through mock-backed internal functions and captured messages.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.h -->
