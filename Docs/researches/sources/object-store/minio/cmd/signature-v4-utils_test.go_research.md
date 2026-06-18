# sources/object-store/minio/cmd/signature-v4-utils_test.go

## Purpose
Tests Signature V4 helper behavior that depends on HTTP request shape, IAM initialization, region compatibility, header canonicalization, and metadata signing requirements.

## Important APIs, Types, And Functions
The file defines `TestCheckValid`, `TestSkipContentSha256Cksum`, `TestIsValidRegion`, `TestExtractSignedHeaders`, `TestSignV4TrimAll`, `TestGetContentSha256Cksum`, and `TestCheckMetaHeaders`.

## Control Flow
`TestCheckValid` builds a filesystem-backed test object layer, initializes config/IAM subsystems, signs a request with root credentials, validates root ownership, checks invalid access-key rejection, creates an IAM user, validates non-owner status, attaches a policy, and verifies policy propagation. Other tests are table-driven over header/query combinations and direct helper calls.

## State And Persistence
This test file creates temporary filesystem state with `prepareFS()`, initializes global MinIO config/IAM subsystems, creates a test IAM user, and attaches policy data. Other tests use in-memory `http.Request` values only. Temporary roots are removed at test cleanup.

## Dependencies And Integration Points
Depends on MinIO test infrastructure (`prepareFS`, `newTestConfig`, subsystem initialization), `madmin-go` user requests, internal auth credential creation, and Signature V4 helper functions. It exercises the integration boundary between request signing helpers and the IAM subsystem.

## Risks And Edge Cases
`TestCheckValid` is more integration-like than pure unit testing and may be sensitive to subsystem initialization timing; it sleeps to allow policy attachment visibility. The metadata test covers headers and query-form metadata, but not multi-valued metadata mismatches. The checksum tests cover presigned detection using `X-Amz-Credential` but not STS body hashing.

## Test Signals
Good regression signal for compatibility behavior around legacy `US` region, Go-stripped headers, broken SHA256 clients, and metadata-signing enforcement. Failures here often imply request authentication compatibility or IAM lookup regressions.
