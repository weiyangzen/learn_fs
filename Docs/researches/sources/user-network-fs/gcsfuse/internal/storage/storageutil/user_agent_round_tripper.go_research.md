## sources/user-network-fs/gcsfuse/internal/storage/storageutil/user_agent_round_tripper.go

Purpose: HTTP RoundTripper middleware that injects a configured User-Agent header when a custom HTTP client is used.

Important APIs/types/functions: `userAgentRoundTripper` with fields `wrapped http.RoundTripper` and `UserAgent string`; method `RoundTrip`.

Control flow: mutates the outgoing request header with `Set("User-Agent", UserAgent)` then delegates to wrapped transport.

State and persistence behavior: no persistent state; mutates request headers in-flight.

Dependencies and integration points: used by `CreateHttpClient` because `option.WithUserAgent` is incompatible with direct `WithHTTPClient` injection.

Risks: panics if `wrapped` is nil. It overwrites any existing User-Agent. Mutating shared requests could surprise callers, although normal `http.Client` use is per request.

Test signals: `client_test.go` verifies a server receives the configured user agent.
