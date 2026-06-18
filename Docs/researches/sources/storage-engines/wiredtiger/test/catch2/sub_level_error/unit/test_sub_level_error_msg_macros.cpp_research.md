# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp

Purpose: Unit tests for last-error message macros `WT_RET_SUB`, `WT_ERR_SUB`, `WT_RET_MSG`, and `WT_ERR_MSG`.

Important helpers/APIs: four small static functions invoke the macros against a `WT_SESSION_IMPL`. The `_SUB` variants set both primary and sub-level error; `_MSG` variants set primary error with `WT_NONE`.

Control flow: a real connection/session is opened, `err_info` is captured, and each section calls one helper with `EINVAL` and a message. Expected results are `EINVAL` return and error-info state matching the macro semantics. `_SUB` tests use `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`; `_MSG` tests assert sub-level remains `WT_NONE`.

State and persistence: per-session `WT_ERROR_INFO` is the only meaningful state. Connection files are wrapper-managed.

Dependencies/integration: covers macro control-flow forms that either return immediately or jump to `err:`. Risks are low, but exact behavior depends on macro expansion and session error-message allocation. Test signals are return code and `check_error_info`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_msg_macros.cpp -->
