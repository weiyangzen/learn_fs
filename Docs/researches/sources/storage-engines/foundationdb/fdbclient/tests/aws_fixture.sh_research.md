# sources/storage-engines/foundationdb/fdbclient/tests/aws_fixture.sh

## Purpose
This Bash fixture provides helper functions for FoundationDB blobstore tests that run against real AWS S3. It creates scratch space, discovers EC2 metadata-derived region/account information, writes blob credential files, and cleans up temporary files.

## Important APIs, Types, And Functions
Key functions are `shutdown_aws`, `create_aws_dir`, `write_blob_credentials`, and `aws_setup`. `write_blob_credentials` either builds and runs the Go `fdb-aws-s3-credentials-fetcher` from the build tree or falls back to IMDS role credentials plus `jq`. `aws_setup` returns host, bucket, credentials file, and region as newline-separated values.

## Control Flow
Consumers source the fixture, call `create_aws_dir`, call `aws_setup build_dir aws_dir`, read the returned array, run tests, and call `shutdown_aws`. Setup obtains an IMDSv2 token, region, account id through `aws sts`, computes `backup-${account_id}-${region}`, prefixes the host with `@` to force credential-file lookup, and writes credentials before printing results.

## State And Persistence Behavior
The fixture persists only temporary local scratch files and generated JSON credentials. It may also build a helper binary in the build tree. It does not create or delete S3 buckets; higher-level tests remove object prefixes.

## Dependencies And Integration Points
It depends on Bash 4+, `curl`, `openssl`, `jq`, optionally Go, optionally `aws`, EC2 IMDS at `169.254.169.254`, and the FoundationDB Docker credential-fetcher source. It integrates with `tests_common.sh` through shared `err` logging and with `s3client_test.sh`/`bulkload_test.sh` through the returned configuration.

## Risks And Edge Cases
The fixture assumes it is running in an AWS environment with metadata access and suitable IAM permissions. Missing `aws` CLI is not checked explicitly before `aws_setup`. Several failures call `exit 1` from a sourced file, which terminates the parent test script. Generated credential files contain sensitive temporary credentials and must remain in scratch storage.

## Test Signals
Signals include successful dependency checks, a non-empty credentials JSON file, correct `@s3.<region>.amazonaws.com` host, expected bucket naming, and successful downstream `s3client`/bulkload operations against S3.
