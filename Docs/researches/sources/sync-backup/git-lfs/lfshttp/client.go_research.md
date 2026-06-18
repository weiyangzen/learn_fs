# sources/sync-backup/git-lfs/lfshttp/client.go

Purpose: Implements the core Git LFS HTTP client: request construction, SSH auth resolution, redirects, retries, extra headers, TLS/proxy transport, protocol selection, and client caching.

Important APIs/types/functions: `Client`, `NewClient`, `NewRequest`, `Do`, `DoWithAccess`, `DoWithRedirect`, `doWithRedirects`, `Transport`, `HttpClient`, `ExtraHeadersFor`, `configureProtocols`, `sshResolveWithRetries`, `newRequestForRetry`, and `deadlineConn`.

Control flow: `NewRequest` optionally resolves SSH metadata through `git-lfs-authenticate`, validates HTTP(S), joins endpoint/suffix, applies SSH headers, Accept, and JSON body. `Do` adds extra headers, gets a cached HTTP client by host/access mode, executes with redirects and error handling. Redirect handling caps chains, resolves relative locations, blocks HTTPS-to-HTTP downgrades, strips Authorization across host changes, and preserves body/context. Transport setup applies proxy, timeouts, activity deadlines, TLS certs/root CAs, HTTP version, cookie jar, and SPNEGO for Negotiate.

State and persistence behavior: Caches `http.Client` instances in `hostClients`, stores URL config and env, may use SSH auth cache, and may attach HTTP stats logger. Reads Git config/env for timeouts, SSL, proxy, cookies, HTTP version, and transfer concurrency.

Dependencies and integration points: Central integration point for `lfsapi`, transfer adapters, `lfshttp` cert/proxy/cookie/stats/verbose/retry helpers, `creds`, `ssh`, SPNEGO, and Go `http.Transport`.

Risks and edge cases: Request bodies must be seekable for tracing/retries; non-seekable bodies with tracing path error. `Close` delegates to `httpLogger.Close`, which is nil-safe through the method. Extra headers are deduplicated to avoid retry duplication. HTTP/2 is TLS-only by config.

Test signals: `client_test.go`, `retries_test.go`, `verbose_test.go`, `stats_test.go`, `proxy_test.go`, `certs_test.go`, and `ssh_test.go` cover major behaviors.
