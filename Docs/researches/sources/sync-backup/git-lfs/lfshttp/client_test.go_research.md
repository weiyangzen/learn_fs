# sources/sync-backup/git-lfs/lfshttp/client_test.go

Purpose: Tests core HTTP client setup, redirect safety, request body marshaling, HTTP protocol selection, SSL verification flags, and extra-header deduplication.

Important APIs/types/functions: Exercises `NewClient`, `NewRequest`, `MarshalToRequest`, `Do`, `configureProtocols`, and `ExtraHeadersFor`.

Control flow: Redirect tests build multiple HTTP/TLS servers for local, external, upgrade, and downgrade redirects. Protocol tests use TLS and non-TLS servers to verify HTTP/2 and HTTP/1.1 behavior. Extra-header test applies headers twice to the same request.

State and persistence behavior: Uses in-memory client transport caches and server counters. Request bodies are marshaled to seekable byte readers and reused through redirects.

Dependencies and integration points: Covers `httptest`, TLS settings, `config.Environment`, URL-specific `http.version`, and `http.extraHeader`.

Risks and edge cases: Confirms Authorization survives same-host redirects but is stripped cross-host, and HTTPS-to-HTTP redirect is refused. Confirms bad HTTP version config fails before requests.

Test signals: Strong signal for redirect and transport policy. Does not cover activity timeout deadlines or cookie jars.
