<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/http_transport.go -->
# sources/sync-backup/restic/internal/backend/http_transport.go

## Purpose
Builds the standard HTTP transport used by HTTP-like backends, including TLS roots, client certificates, unix-socket transport support, HTTP/2 tuning, debug wrapping, user-agent injection, and optional stuck-request watchdog behavior.

## Important APIs, Types, And Functions
TransportOptions, readPEMCertKey, and Transport are the important API surface. Transport returns an http.RoundTripper configured from options and feature flags.

## Control Flow
Transport starts from net/http defaults, configures HTTP/2, registers unixtransport, applies TLS options, wraps with the custom user-agent round tripper, optionally wraps with a watchdog, then with debug.RoundTripper.

## State And Persistence Behavior
No repository state is persisted. It reads certificate files from disk and mutates tls.Config on the returned transport.

## Dependencies And Integration Points
Depends on crypto/tls/x509/pem, net/http, x/net/http2, peterbourgon/unixtransport, internal debug/errors/feature, and httpuseragent/watchdog helpers in package backend.

## Risks And Edge Cases
Bad PEM parsing, multiple private keys, empty root cert filenames, InsecureSkipVerify, and feature-flag-specific HTTP/2 timeout behavior are the main risks. Panics if http2 transport configuration unexpectedly fails.

## Test Signals
Covered indirectly by HTTP backend tests and specifically by user-agent tests; certificate parsing and watchdog paths rely mostly on integration coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/http_transport.go -->
