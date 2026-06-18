# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_exclude_regex_test.go

Purpose: Verifies that file-cache exclude regex rules prevent caching even when range reads are enabled.

Important APIs/types/functions: `cacheFileForExcludeRegexTest` carries flags, storage client, context, and base test name. Setup helpers configure log/cache dir and mount. `TestReadsForExcludedFile` uses `setupFileInTestDir`, `readChunkAndValidateObjectContentsFromGCS`, structured read logs, `validate`, and `validateFileIsNotCached`.

Control flow: each test run truncates the log, removes cache dir, creates a unique test directory and file, performs two range reads at different offsets, then checks both logs are cache misses and no cached file exists. The runner uses config flag sets and adds only-dir-specific exclude-regex variants.

State/persistence: Cache directory state is deliberately cleared per test and inspected after reads. GCS content is created through the storage client, read through the mount, and compared with backend chunks.

Dependencies/integration: Uses read-cache package globals, setup/client/operations helpers, structured read-log parser, and testify suite.

Risks/test signals: Regex construction differs for only-dir mount and dynamic bucket paths. Passing signals exclude regex takes precedence over range-read caching.
