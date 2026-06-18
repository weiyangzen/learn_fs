# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp

## sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp

Purpose: Implementation of a lightweight mock `WT_SESSION_IMPL` owner with event-handler capture.

Important functions: constructor installs `handle_wiredtiger_error`/`handle_wiredtiger_message` in an `event_handler_wrap`. Destructor cleans block manager session, terminates file system layer, frees dhandle/btree, error message, scratch buffers, and session. `build_test_mock_session` allocates session, builds mock connection, wires public connection pointer, and returns shared ownership. `setup_block_manager_session` initializes random state and block manager session. `setup_block_manager_file_operations` allocates dhandle/btree. Error/message handlers append callback messages to the mock.

State and persistence: owns in-memory session and shared mock connection. Captures messages in `_messages`; exposes `get_last_message`. No real DB home.

Dependencies/integration: underpins many internal unit tests. Risks include raw internal allocation/free, dhandle ownership assumptions, and `get_last_message` requiring at least one message. Test signals are internal API return codes and captured event messages.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/mock_session.cpp -->
