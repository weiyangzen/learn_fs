# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp

Purpose: Unit tests for `__wt_session_set_last_error` and `__wt_session_reset_last_error`.

Important APIs/types: real `WT_SESSION_IMPL`, `WT_ERROR_INFO`, sub-level codes including `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_CONFLICT_BACKUP`, `WT_UNCOMMITTED_DATA`, and `WT_DIRTY_DATA`.

Control flow: sections verify null-session reset is safe, reset initializes success values, set stores `EINVAL` plus sub-level code/message, subsequent set does not overwrite an existing error until reset, multiple set/reset cycles work for different primary/sub-level pairs, and a 1024-byte message is stored and compared.

State and persistence: only `session_impl->err_info` changes. Connection files are wrapper-managed. The non-overwrite behavior is the central persistence rule within a session error lifecycle.

Dependencies/integration: depends on error-message allocation/copy and reset freeing/replacing prior state. Risks include exact large-message behavior and non-overwrite semantics being surprising to callers. Test signals are `check_error_info` after each mutation.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_session_set_last_error.cpp -->
