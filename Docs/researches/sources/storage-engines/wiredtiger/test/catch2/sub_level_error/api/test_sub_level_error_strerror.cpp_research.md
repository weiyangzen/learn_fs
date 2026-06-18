# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp

Purpose: Public API coverage for `wiredtiger_strerror` when passed WiredTiger sub-level error codes.

Important APIs/types: `check_error_code` converts an integer error code to `std::string` through `wiredtiger_strerror` and compares it to the expected symbolic description.

Control flow: one section iterates a vector of `(code, expected string)` pairs for all listed sub-level codes: `WT_NONE`, background compact already running, cache overflow, write conflict, oldest-for-eviction, backup/dhandle/schema/table/checkpoint/live-restore/disaggregated conflicts, uncommitted data, and dirty data.

State and persistence: stateless API mapping test; no connection/session is opened.

Dependencies/integration: integrates public error-code rendering with the sub-level error enum namespace. Risks are exact-string brittleness and incomplete coverage if new sub-level codes are added without updating this vector. Test signals are exact string comparisons.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/api/test_sub_level_error_strerror.cpp -->
