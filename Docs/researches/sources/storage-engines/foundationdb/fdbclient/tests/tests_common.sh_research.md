# sources/storage-engines/foundationdb/fdbclient/tests/tests_common.sh

## Purpose
This file centralizes Bash helper functions used by FoundationDB blobstore and bulkload CTests. It covers logging, cleanup watchdogs, preserve-data behavior, FDB data loading/verification, severity log scans, encryption key generation, provider detection, blobstore environment setup, and TLS CA discovery.

## Important APIs, Types, And Functions
Important helpers include `start_cleanup_watchdog`, `cancel_cleanup_watchdog`, `log`, `err`, `output_contains`, `output_matches`, `should_preserve_test_data`, `cleanup_with_preserve_check`, `make_key`, `has_data`, `has_nodata`, `load_data`, `clear_data`, `verify_data`, `is_fdb_source_dir`, `log_test_result`, `grep_for_severity40`, `test_fdbcli_status_json_for_bkup`, `create_encryption_key_file`, `get_use_s3_default`, `detect_blobstore_provider`, `setup_s3_environment`, and `setup_tls_ca_file`.

## Control Flow
Data helpers build deterministic key names from `FDB_KEY_PREFIX`, write timestamped values through `fdbcli`, clear the whole keyspace with `clearrange "" \xff`, and verify each stored value. Environment setup chooses GCS if GCS credentials are present, real S3 if `USE_S3=true`, otherwise MockS3Server, then sources the right fixture, creates scratch space, starts mock services as needed, builds `host`, `bucket`, `region`, `blob_credentials_file`, and `query_str`, and exports credentials/TLS variables for FoundationDB processes.

## State And Persistence Behavior
Global state includes `FDB_DATA`, `FDB_DATA_KEYCOUNT`, `FDB_KEY_PREFIX`, `TESTS_COMMON_DIR`, `CLEANUP_WATCHDOG_PID`, and provider variables made readonly by setup. It mutates the test database during load/clear operations and writes credential/key files in scratch directories. The watchdog can forcibly terminate process groups if cleanup exceeds its budget.

## Dependencies And Integration Points
The file integrates all S3/GCS/MockS3 fixtures and FDB cluster tests. It depends on `fdbcli`, `jq`, shell process tools, CA bundle paths, and Ginkgo-style CTest invocation around the scripts.

## Risks And Edge Cases
The cleanup watchdog has a broad `pkill -f` fallback based on script name, which is useful for hung CTests but dangerous if names collide. `verify_data` parses `fdbcli get` output with `sed`, making it sensitive to output format and punctuation. `setup_s3_environment` marks globals readonly, so callers cannot reconfigure after setup in the same shell.

## Test Signals
Signals are accurate pass/fail logs, successful FDB data round trips, provider-specific environment variables exported, preserved scratch paths printed when requested, and `grep_for_severity40` returning failure on high-severity traces.
