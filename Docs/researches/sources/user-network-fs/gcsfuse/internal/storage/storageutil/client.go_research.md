## sources/user-network-fs/gcsfuse/internal/storage/storageutil/client.go

Purpose: Defines storage client configuration and constructs HTTP clients/token sources for gcsfuse storage backends.

Important APIs/types/functions: `StorageClientConfig` carries protocol, endpoint, auth, retry, HTTP, gRPC, tracing, DNS cache, metrics, GKE, and write settings. `ConfigureDialerWithLocalAddr`, `CreateHttpClient`, `CreateTokenSource`, and `StripScheme` are the main functions.

Control flow: `CreateHttpClient` builds a `net.Dialer`, optionally binds `LocalSocketAddress`, optionally installs a caching DNS resolver, creates HTTP/1 or HTTP/2 transport, then either returns an anonymous timeout-only client or wraps transport with OAuth2, user-agent middleware, and optional OpenTelemetry HTTP tracing.

State and persistence behavior: no persistent state. It may resolve local socket addresses and may use auth/token providers. Client configuration determines connection pooling, keepalive, timeout, and tracing state.

Dependencies and integration points: integrates `cfg.Protocol`, internal auth token source, metrics handle, DNS cache package, oauth2 transport, `userAgentRoundTripper`, and OpenTelemetry HTTP instrumentation. Called by storage handle creation.

Risks: anonymous access path intentionally omits custom transport and user-agent injection, which affects observability and local socket/DNS behavior. HTTP/2 disables keepalives and ignores some HTTP/1 tuning assumptions. `StripScheme` preserves Google internal schemes and only splits the first generic scheme separator.

Test signals: `client_test.go` covers HTTP client creation, token source creation, scheme stripping, tracing span generation, user-agent/auth headers, and socket-address success/failure.
