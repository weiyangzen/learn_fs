## sources/user-network-fs/gcsfuse/internal/storage/storageutil/client_test.go

Purpose: Tests storage HTTP client configuration helpers.

Important APIs/types/functions: `clientTest`, `newInMemoryExporter`, and test methods for HTTP/1/HTTP/2 creation, auth-enabled creation, token source creation, `StripScheme`, HTTP tracing, user-agent/auth header propagation, local socket binding, and invalid socket address handling.

Control flow: uses default test config from `test_util.go`, mutates relevant fields, invokes `CreateHttpClient` or `CreateTokenSource`, and validates client timeout, headers, spans, or connection source address through local `httptest` servers.

State and persistence behavior: sets global OpenTelemetry tracer provider for tracing tests with cleanup reset. Reads `testdata/key.json`; local servers are closed per test.

Dependencies and integration points: asserts that `CreateHttpClient` composes oauth2, user-agent middleware, and OpenTelemetry HTTP transport correctly. The socket test checks real `net.Dialer.LocalAddr` behavior.

Risks: tests use real networking on loopback and timing-sensitive span collection; they do not introspect transport internals for HTTP/1 versus HTTP/2 settings.

Test signals: strong guard for external request behavior: user-agent, bearer token, trace spans, scheme preservation, and bind address errors.
