<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3_test.go -->
# sources/sync-backup/restic/internal/backend/s3/s3_test.go

## Purpose
Integration-tests and benchmarks the S3 backend against MinIO or configured S3 credentials.

## Important APIs, Types, And Functions
runMinio, newMinioTestSuite, TestBackendMinio, BenchmarkBackendMinio, newS3TestSuite, TestBackendS3, and BenchmarkBackendS3 are key.

## Control Flow
Tests start a MinIO process when available, wait for TCP readiness, create randomized credentials/prefixes, and run the generic backend suite. Separate tests use RESTIC_TEST_S3_* environment variables for real S3.

## State And Persistence Behavior
Uses external processes, temporary directories, network sockets, and environment credentials.

## Dependencies And Integration Points
Depends on minio binary, backend/test Suite, location factory, options.SecretString, and internal/test.

## Risks And Edge Cases
Skipped without binaries/env vars; fixed port 9000 can conflict on shared hosts.

## Test Signals
Provides broad contract coverage for S3 persistence behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/s3_test.go -->
