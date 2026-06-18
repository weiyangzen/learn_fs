<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_test.go -->
# sources/object-store/minio/cmd/generic-handlers_test.go

## Purpose
Tests selected generic HTTP handler helpers: RPC request detection, header-size enforcement, reserved metadata blocking, SSE-C TLS enforcement, and bad path component scanning performance.

## Important APIs, types, and functions
- `TestGuessIsRPC` checks legacy `/minio/lock` and current grid route paths.
- `generateHeader`, `isHTTPHeaderSizeTooLargeTests`, and `TestIsHTTPHeaderSizeTooLarge` build limit-boundary headers.
- `containsReservedMetadataTests` and `TestContainsReservedMetadata` distinguish internal reserved metadata from permitted crypto/replication headers.
- `sseTLSHandlerTests` and `TestSSETLSHandler` validate `setRequestValidityMiddleware` SSE-C behavior under TLS and non-TLS.
- `Benchmark_hasBadPathComponent` covers path scanner cases and throughput.

## Control flow
Tests construct synthetic requests/headers, call helper functions or wrap an OK handler with middleware, and compare booleans or HTTP response codes. `TestSSETLSHandler` temporarily mutates `globalIsTLS` and restores it with a deferred closure.

## State and persistence behavior
No persistence. The only global mutation is `globalIsTLS` during SSE-C middleware testing.

## Dependencies and integration points
Depends on request auth helpers, grid route constants, crypto metadata constants, HTTP test recorder, and generic middleware functions from `generic-handlers.go`.

## Risks and edge cases
Coverage is focused and does not test reserved bucket blocking, host validation, federation forwarding, browser redirect, metrics auth precedence, multiple-auth detection, or upload forwarding. Header size generation approximates sizes through key lengths.

## Test signals
Signals are true/false classifier results, exact HTTP 200 vs error behavior for SSE-C over TLS/plain HTTP, metadata limit boundary booleans, reserved metadata booleans, and benchmark failures if path scanning returns unexpected results.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers_test.go -->
