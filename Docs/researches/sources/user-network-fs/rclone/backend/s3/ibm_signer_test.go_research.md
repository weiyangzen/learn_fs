# sources/user-network-fs/rclone/backend/s3/ibm_signer_test.go

## Purpose
IBM signer unit test: verifies IAM signer header setting with a mock authenticator.

## Important APIs, Types, And Functions
Important surface: MockAuthenticator, TestSignHTTP.

## Control Flow
constructs request, signs it, asserts Authorization and instance-id headers

## State And Persistence
in-memory only.

## Dependencies And Integration Points
Go test/http/time/context and AWS credentials.

## Risks And Test Signals
Risks and useful test signals: happy path only; missing token-error/no-op provider coverage.
