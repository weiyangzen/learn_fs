# sources/object-store/minio/cmd/object-handlers-common_test.go

## Purpose
This test file verifies selected shared object-handler precondition helpers. It focuses on ETag canonicalization and S3-compatible conditional GET/HEAD precedence for `If-None-Match`, `If-Modified-Since`, `If-Match`, and `If-Unmodified-Since`.

## Important APIs, types, and functions
- `TestCanonicalizeETag` checks quote stripping behavior for unusual and ordinary ETag strings.
- `TestCheckPreconditions` builds HEAD requests with conditional headers, passes a fixed `ObjectInfo`, and asserts both the boolean "request should stop" result and the recorded HTTP status code.

## Control flow
The first test table in `TestCheckPreconditions` covers cases where `If-None-Match` matches or `If-Modified-Since` indicates no modification. The expected outcome is `true` with HTTP 304. The second table covers cases where `If-Match` succeeds while `If-Unmodified-Since` would otherwise be problematic; the expected outcome is to proceed with no status override, leaving the recorder at its default 200.

## State and persistence behavior
The tests are pure HTTP helper tests. They use `httptest.NewRecorder`, in-memory requests, and a fixed `ObjectInfo{ETag: "aa", ModTime: ...}`. No object layer or persistent storage is touched.

## Dependencies and integration points
The file depends on `checkPreconditions`, `canonicalizeETag`, `ObjectInfo`, `ObjectOptions`, and MinIO HTTP header constants. It protects behavior that GET and HEAD handlers in `object-handlers.go` rely on before serving object bytes or headers.

## Risks and edge cases
The tests cover only a subset of conditional behavior. They do not validate failing `If-Match`, failing `If-Unmodified-Since` when `If-Match` is absent, part-number validation, copy-source preconditions, or PUT preconditions. The chosen timestamp is fixed and tests the one-second HTTP date precision behavior indirectly.

## Test signals
The file gives focused regression signal for the conditional precedence that is easy to break during refactoring. Broader handler-level tests are still needed for complete S3 compatibility.
