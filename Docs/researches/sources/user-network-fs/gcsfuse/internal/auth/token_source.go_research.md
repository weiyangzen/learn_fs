<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/token_source.go

Purpose: token-source implementation backed by an HTTP or Unix-socket token endpoint, with optional oauth2 token reuse.

Important APIs/types/functions: `newProxyTokenSource`, `proxyTokenSource.Token`, and exported `NewTokenSourceFromURL`.

Control flow: URL parsing selects a normal HTTP client or a custom Unix-socket transport. `Token` performs GET, reads at most 1 MiB, converts non-2xx responses into `oauth2.RetrieveError`, and JSON-decodes the response into `oauth2.Token`.

State and persistence: the proxy source itself is stateless. If `reuseTokenFromUrl` is true, `oauth2.ReuseTokenSource` wraps it and caches valid tokens in memory.

Dependencies: net/http, net/url, Unix-socket dialing through `net.Dialer`, oauth2 token types, endpoint availability, and caller context at construction time.

Risks: `Token` uses `client.Get(ts.endpoint)` and does not pass the stored context into the request, so cancellation may not affect HTTP GETs. Endpoint responses are trusted to provide token JSON. The 1 MiB body limit avoids unbounded memory use but may truncate unusual errors.

Test signals: `token_source_test.go` covers successful HTTP token fetch, invalid URL, server error, and invalid JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source.go -->
