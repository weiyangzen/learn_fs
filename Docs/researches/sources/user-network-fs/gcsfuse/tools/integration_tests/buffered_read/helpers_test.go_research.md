<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go

Purpose: Shared helpers for buffered-read integration tests, covering file setup, direct reads, GCS validation, and buffered-read log parsing.

Important APIs, types, and functions: `Expected` captures expected log attributes. `readFileAndValidate` performs full or chunk reads and validates CRC32C or object chunk content. `validate` checks log entry timestamps, bucket/object names, and fallback flag. `setupFileInTestDir`, `parseBufferedReadLogs`, `parseAndValidateSingleBufferedReadLog`, `readAndValidateChunk`, and `induceRandomReadFallback` support the suites.

Control flow: Read helpers create expected metadata before the read, perform mounted filesystem reads using `O_DIRECT`, compare data with Cloud Storage, then record end timestamps. Log helpers open the configured log file and parse buffered read entries, expecting one entry for single-handle tests.

State and persistence behavior: Reads mounted files, creates test files via GCS client, opens log files, and depends on global `testEnv` and setup flags. It does not clean up itself.

Dependencies and integration points: Integrates Cloud Storage object validation, gcsfuse log parser `read_logs`, operations helpers, setup bucket selection including dynamic bucket mounts, and the buffered read test suites.

Risks and test signals: Timestamp assertions use seconds and only check start lower bound; delayed log flushing can affect parsing. CRC32C full-file validation gives strong data integrity signal. Random fallback induction assumes threshold and block-size behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/helpers_test.go -->
