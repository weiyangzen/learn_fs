<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3_test.go -->
# sources/sync-backup/kopia/cli/storage_s3_test.go

## Purpose
Unit tests for S3 custom root CA loading from base64 and file path.

## Important APIs, Types, And Functions
Defines fake cert bytes and tests `preActionLoadPEMBase64`, `preActionLoadPEMPath`, and mutual exclusion when both base64 and path are used.

## Control Flow
The tests instantiate `storageS3Flags` directly, set fields, invoke pre-actions, and assert RootCA bytes or expected errors.

## State And Persistence Behavior
No repository or network state is used. Temporary files hold fake certificate content for path loading.

## Dependencies And Integration Points
Integrates the S3 flag helper functions, base64 encoding, temp directories, and testify assertions.

## Risks And Edge Cases
The tests do not validate that bytes are real PEM data; they only check transport into options. Mutual exclusion depends on invocation order.

## Test Signals
Good signal for CLI pre-action behavior. Backend TLS behavior and connect-time S3 options need separate integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_s3_test.go -->
