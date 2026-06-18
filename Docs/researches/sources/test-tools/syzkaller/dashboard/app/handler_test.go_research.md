# sources/test-tools/syzkaller/dashboard/app/handler_test.go

Purpose: unit tests for `gzipResponseWriterCloser`, the response adapter used by UI middleware.

Important APIs/types/functions: `TestGzipResponseWriterCloser_no_compression`, `TestGzipResponseWriterCloser_with_compression`, `TestGzipResponseWriterCloser_headers`, `TestGzipResponseWriterCloser_status`, and `httpRequestWithAcceptedEncoding`.

Control flow: tests write a short payload, call `writeResult` with/without gzip support, check body/header behavior, and verify wrapper header/status forwarding.

State/persistence: in-memory `httptest.ResponseRecorder` and gzip buffers only.

Dependencies/integration: standard `compress/gzip`, `net/http`, `httptest`, and `testify/assert`; integration point is `handleContext`.

Risks/test signals: tests do not cover oversized plain responses or error paths, but they protect the core success behavior for gzip and non-gzip clients.
