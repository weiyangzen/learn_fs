# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp

Purpose: Tests how nested API calls affect session last-error state, especially `WT_NOTFOUND` handling inside top-level API flow.

Important APIs/types: `CURSOR_API_CALL`, `SESSION_API_CALL_NOCONF`, `WT_ERR_NOTFOUND_OK`, `WT_ERR`, `API_END_RET`, `__wt_session_set_last_error`, and a real table cursor.

Control flow: `cursor_api_call_with_notfound` simulates cursor `next` returning `WT_NOTFOUND` and optionally explicitly sets last error. `api_call_nested_with_notfound` invokes that nested cursor API either through `WT_ERR_NOTFOUND_OK` or `WT_ERR`, then optionally simulates a later `EINVAL`. Sections cover combinations of notfound-ok vs notfound-error, final error zero vs EINVAL, and nested explicit err_info vs implicit error-only return.

State and persistence: creates a table and cursor; session `err_info` is the core state. Explicitly set nested error info can be preserved across later top-level errors in selected paths.

Dependencies/integration: validates subtle API nesting rules, error discard behavior, and cursor/table setup. Risks are high semantic complexity and exact expected precedence. Test signals are top-level return code plus error-info content.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_nested_api_calls.cpp -->
