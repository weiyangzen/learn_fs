# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp

Purpose: Shared Catch2 helper implementation for sub-level error tests.

Important functions: `utils::prepare_session_and_error` opens a public session from a `connection_wrapper`, asserts success, and returns both `WT_SESSION *` and a pointer to the internal `WT_ERROR_INFO`. `utils::check_error_info` compares primary error, sub-level error, and error message string.

Control flow: helpers are intentionally small and assertion-heavy. `prepare_session_and_error` relies on the wrapper's `WT_CONNECTION` and casts the opened session to `WT_SESSION_IMPL` to expose `err_info`. `check_error_info` performs three Catch2 `CHECK` assertions, including `strcmp` on the message.

State and persistence: opens sessions on real connections and exposes mutable per-session error state to tests. It does not own or close sessions; connection lifetime is managed by the caller's wrapper.

Dependencies/integration: used by API/drop/compact/rollback sub-level tests. Risks include raw pointer exposure and assuming `err_msg` is non-null when passed to `strcmp`. Test signals are helper assertions embedded in calling tests.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.cpp -->
