# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h

Purpose: Declaration header for shared sub-level error test helpers.

Important APIs/types: includes Catch2, `wt_internal.h`, and `connection_wrapper.h`; declares `utils::prepare_session_and_error(connection_wrapper *, WT_SESSION **, WT_ERROR_INFO **)` and `utils::check_error_info(WT_ERROR_INFO *, int, int, const char *)`.

Control flow/state: no runtime control flow beyond declarations. Its role is to standardize how tests open sessions and assert `WT_ERROR_INFO` triples.

Dependencies/integration: included by API and unit tests in `sub_level_error`. It creates a dependency from test files to the C++ connection wrapper and internal `WT_ERROR_INFO` type. Risks are broad rebuild coupling and potential namespace/helper name collisions if other test utilities add similar functions. Test signals are indirect through the implementation's Catch2 assertions.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/utils_sub_level_error.h -->
