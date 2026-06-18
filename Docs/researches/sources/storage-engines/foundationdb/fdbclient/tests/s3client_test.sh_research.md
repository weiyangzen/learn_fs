# sources/storage-engines/foundationdb/fdbclient/tests/s3client_test.sh

## Purpose
This integration test exercises the FoundationDB `s3client` binary against real S3, MockS3Server, or mock-GCS mode. It validates file copy, directory copy, listing behavior, missing resources, and optional object-integrity checks.

## Important APIs, Types, And Functions
Major functions are `cleanup`, `filter_http_debug`, `run_s3client`, `resolve_to_absolute_path`, `upload_download`, `test_file_upload_and_download`, `test_file_upload_and_download_no_integrity_check`, `test_dir_upload_and_download`, `test_nonexistent_bucket`, `test_nonexistent_resource`, `test_empty_bucket`, `wait_for_files_in_listing`, `test_list_with_files`, and `test_ls_handling`.

## Control Flow
The script installs traps, sources `tests_common.sh`, determines `USE_S3`, parses optional explicit S3 settings, validates the build/scratch arguments, selects real S3, mock GCS, or MockS3Server, builds blobstore URL query strings, and runs the test cases. `run_s3client` centralizes common flags including HTTP verbosity, optional KMS encryption for real S3, integrity-check knob, TLS CA file, blob credentials, and log directory. Upload/download tests copy local files/directories up to blobstore, copy them back, remove the remote prefix, and `diff` local results. Listing tests account for S3 vs MockS3/Seaweed differences and include retry loops for eventual listing visibility.

## State And Persistence Behavior
The script creates scratch files, logs, credentials JSON, and optional MockS3 persisted objects. Remote state is created and removed under per-test path prefixes. Cleanup shuts down MockS3/AWS scratch unless preservation is requested.

## Dependencies And Integration Points
It depends on built `bin/s3client`, cloud/mock fixtures, shared helper matching functions, `diff`, `grep`, `awk`, and blobstore URL parsing by FoundationDB. It can use explicit `--host`, `--bucket`, `--region`, and `--blob-credentials-file` in real S3 mode.

## Risks And Edge Cases
The script’s behavior branches heavily by provider, so an assertion meaningful for S3 may be too loose for MockS3 or vice versa. HTTP debug filtering is text-pattern based and can mask output changes. Some checks only inspect command output rather than object metadata. The final `fi`/test block indentation is unusual but syntactically part of provider setup completion.

## Test Signals
Strong signals are successful round-trip `diff`, successful recursive and non-recursive listings with expected paths, correct empty/missing resource behavior for each provider, and clean remote-prefix removal after each test.
