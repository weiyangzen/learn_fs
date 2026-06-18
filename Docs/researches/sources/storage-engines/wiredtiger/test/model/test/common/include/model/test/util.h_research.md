# sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/util.h

Purpose: declares general model test helper utilities and assertions.

Important APIs and types: macro `model_testutil_assert_exception`; functions `create_tmp_file`, `current_time`, test-level `parse_uint64`, `parse_uint64_range`, `trim`, `verify_using_debug_log`, and `verify_workload`.

Control flow: exception assertion executes a call and fails via `testutil_die` unless the requested exception type is thrown. Parsing and trim helpers are direct utilities. `verify_using_debug_log` and `verify_workload` orchestrate full model/WT comparison flows implemented in `common/util.cpp`.

State and persistence: temporary files are created by `create_tmp_file`; verification helpers create or open WT homes and may generate debug-log JSON files. No global model state is stored in the header.

Dependencies and integration: includes `kv_workload.h`, `model/util.h`, and C `test_util.h`. It is part of `wiredtiger_model_test_common` public includes.

Risks: `parse_uint64` duplicates model namespace functionality for convenience until refactoring. Verification helpers assume valid WT test options and home paths. Temporary file helper creates a file even when only a name is needed.

Test signals: used across model tests for exception checks, workload validation, debug-log validation, range parsing, and timing.
