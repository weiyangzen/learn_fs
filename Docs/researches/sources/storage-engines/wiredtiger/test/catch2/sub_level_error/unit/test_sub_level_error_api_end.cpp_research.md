# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp

Purpose: Unit tests for API-end macros preserving or resetting session last-error information: `API_END_RET` and `TXN_API_END`.

Important helpers/APIs: `api_call_with_error` wraps `SESSION_API_CALL_NOCONF`, optional `__wt_session_set_last_error`, and `API_END_RET`. `txn_api_call_with_error` wraps `SESSION_TXN_API_CALL` and `TXN_API_END`. Shared `check_error_info` verifies `WT_ERROR_INFO`.

Control flow: the test opens a real session, then exercises no-error, primary-error-only, error with message, repeated message, different messages, and EBUSY with different sub-level errors. It repeats analogous coverage for transaction API end paths.

State and persistence: state is `session_impl->err_info`. Successful API completion resets to success; errors without explicit messages produce `WT_ERROR_INFO_EMPTY`; explicit last errors preserve primary code, sub-code, and message through API-end macros. Connection files are created and cleaned by wrapper.

Dependencies/integration: depends on WiredTiger public connection/session and internal API macros. Risks include macro-flow fragility and exact behavior around repeated messages. Test signals are return codes plus `WT_ERROR_INFO` contents after each API call.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_api_end.cpp -->
