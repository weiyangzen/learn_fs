<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go -->
# sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go

## Purpose
Provides a small RoundTripper decorator that overwrites the User-Agent header for every outgoing HTTP request.

## Important APIs, Types, And Functions
httpUserAgentRoundTripper, newCustomUserAgentRoundTripper, and RoundTrip implement the decorator.

## Control Flow
RoundTrip clones the request with its context, sets User-Agent, and delegates to the wrapped RoundTripper.

## State And Persistence Behavior
No persistence. The only state is the configured userAgent string and wrapped transport reference.

## Dependencies And Integration Points
Depends only on net/http and is consumed by Transport when TransportOptions.HTTPUserAgent is non-empty.

## Risks And Edge Cases
If the wrapped transport is nil, RoundTrip will panic; callers construct it through Transport with a concrete base transport. Cloning avoids mutating shared request state.

## Test Signals
Directly tested by httpuseragent_roundtripper_test.go with an httptest server checking the header.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/httpuseragent_roundtripper.go -->
