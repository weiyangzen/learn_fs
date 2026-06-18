# Research: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp

## sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp

Purpose: RAII wrapper implementation for real WiredTiger connections used by Catch2 tests.

Important functions: constructor validates/creates the DB home directory, opens WiredTiger with `wiredtiger_open`, and stores both public and internal connection pointers. Destructor closes the connection and optionally calls `utils::wiredtiger_cleanup`. `create_session` opens a session and returns it as `WT_SESSION_IMPL *`. Accessors expose public/internal connection pointers.

Control flow: constructor checks `stat`, rejects an existing non-directory path, creates missing directory with `mkdir`, then opens with supplied config. Destructor throws through `throw_if_non_zero` if close fails. `create_session` does not check the return code explicitly.

State and persistence: owns a real database home and connection. It creates WiredTiger files and removes them unless `_do_cleanup` is cleared.

Dependencies/integration: central to tests that need real engine behavior. Risks include destructor throwing during stack unwinding, unchecked `open_session` return, and cleanup file-list incompleteness. Test signals are failures via thrown runtime errors or WT return assertions in callers.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/wrappers/connection_wrapper.cpp -->
