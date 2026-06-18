# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp

Purpose: Public API test for `WT_SESSION::get_last_error`, focused on default session error-info state.

Important APIs/types: `connection_wrapper` opens a real connection, `conn->open_session` creates a public `WT_SESSION`, and `session->get_last_error` fills `err`, `sub_level_err`, and `err_msg`.

Control flow: the test creates a connection in the current directory with `create`, opens a session, calls `get_last_error` before any failure, and asserts default values: primary error `0`, sub-level error `WT_NONE`, and message `WT_ERROR_INFO_SUCCESS`.

State and persistence: the underlying connection creates WiredTiger files through `connection_wrapper`; error state is per-session and initially reset. No table data is created.

Dependencies/integration: validates that public API surfaces the internal `WT_ERROR_INFO` initialization contract. It depends on `utils_sub_level_error.h` only for shared declarations and on connection cleanup. Risks are minimal but it only covers defaults, not non-default API retrieval. Test signals are exact returned values from `get_last_error`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_session_get_last_error.cpp -->
