<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go -->
# sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go

## Purpose
Tests that the custom user-agent RoundTripper injects the configured User-Agent on outgoing requests.

## Important APIs, Types, And Functions
TestCustomUserAgentTransport is the only test.

## Control Flow
An httptest server validates the header, a client uses httpUserAgentRoundTripper, and the test asserts HTTP 200 response status.

## State And Persistence Behavior
No persistent state; uses an in-memory test server and closes response bodies.

## Dependencies And Integration Points
Depends on net/http, net/http/httptest, testing, and package-local round tripper type.

## Risks And Edge Cases
The test validates header setting but not request cloning or nil wrapped transport behavior.

## Test Signals
Provides focused unit coverage for custom user-agent injection used by HTTP transports.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper_test.go -->
