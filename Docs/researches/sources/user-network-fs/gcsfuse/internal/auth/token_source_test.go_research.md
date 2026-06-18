<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go

Purpose: tests proxy token-source URL parsing and token-fetch error handling.

Important APIs/types/functions: `Test_NewTokenSourceFromURL_Success`, `Test_NewTokenSourceFromURL_InvalidURL`, `TestProxyTokenSource_TokenFetch_ServerError`, and `TestProxyTokenSource_TokenFetch_InvalidJSON`.

Control flow: httptest servers return token JSON, HTTP 500 text, or invalid JSON; tests construct a source and call `Token` to validate returned token or error contents.

State and persistence: in-memory httptest servers only; no real credentials or network services beyond loopback.

Dependencies: `httptest`, JSON encoder, oauth2 token type, testify.

Risks: tests do not cover Unix-socket URLs, reuse-token caching, body limit behavior, or request cancellation.

Test signals: run `go test ./internal/auth -run TokenSource`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/token_source_test.go -->
