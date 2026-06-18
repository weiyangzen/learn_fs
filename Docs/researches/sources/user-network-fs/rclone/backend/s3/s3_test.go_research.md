# sources/user-network-fs/rclone/backend/s3/s3_test.go

## Purpose
This file contains package-level tests for the S3 backend and wires the backend into rclone's generic integration test suite. It focuses on HTTP redirect security behavior, AWS dual-stack option mapping, generic backend conformance, directory marker config coverage, cutoff setter interfaces, and Object Lock retain-date parsing.

## Important APIs, Types, And Functions
`SetupS3Test` builds a minimal AWS-provider `Options` plus the backend HTTP client. Four redirect tests validate `s3CheckRedirect`: security tokens are stripped when a redirect crosses hosts, remain stripped for later redirects, are preserved for same-host redirects, and redirect loops stop after ten hops.

`TestIntegration` and `TestIntegration2` call `fstests.Run` with `NilObject: (*Object)(nil)`, storage tier expectations, minimum chunk size, and optional directory marker config. `TestAWSDualStackOption` checks that `UseDualStack` maps to AWS SDK endpoint options. Exported wrappers `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` expose private setters to `fstests` interfaces. `TestParseRetainUntilDate` validates RFC3339 inputs, timezone offsets, duration inputs, and invalid strings.

## Control Flow
Redirect tests set up `httptest.Server` instances and send requests through the backend-created client, asserting headers observed by servers. Integration tests rely on external rclone remote configuration unless skipped by `fstest.RemoteName`. Dual-stack tests create SDK clients with and without the option and inspect the resulting SDK client options. Retain-date parsing tests capture `now` once and allow small timing tolerance for duration-derived dates.

## State And Persistence Behavior
Most tests are local and ephemeral. Generic integration tests create and delete remote objects and buckets through `fstests`. `TestIntegration2` only runs when a specific remote is not supplied and injects `directory_markers=true` into the test config. Redirect tests do not persist state beyond temporary HTTP servers.

## Dependencies And Integration Points
The file integrates with `net/http/httptest`, AWS SDK endpoint option constants, rclone `fs` option interfaces, `fstest`/`fstests`, and testify. It directly tests unexported backend functions and also asserts that `*Fs` satisfies upload/copy cutoff setter interfaces used by generic tests.

## Risks And Edge Cases
The redirect security tests are important because AWS session tokens should not be forwarded to different hosts after S3/CDN redirects. If redirect logic changes to compare only adjacent redirects instead of the original chain, the cross-host second-hop test can catch leakage. Integration tests depend on external credentials and provider behavior, so they may be skipped or provider-specific. Duration-based retain-date tests are tolerant but still time-sensitive.

## Test Signals
This file gives fast local coverage for redirect behavior and parser/setter logic, plus broad remote coverage through `fstests.Run`. It is the main public conformance entry point for the S3 backend.
