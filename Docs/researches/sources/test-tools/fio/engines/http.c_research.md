# sources/test-tools/fio/engines/http.c

Purpose: Implements a synchronous diskless HTTP(S) engine using libcurl easy APIs for WebDAV-style, S3, and Swift object IO.

Important APIs/functions: Registers `http` engine with setup, queue, cleanup, event stubs, open, and invalidate callbacks. Options configure HTTPS mode, host, basic auth, S3 credentials/security token/region/SSE/storage class, Swift token, mode, verbosity, and object mode. Helpers implement AWS URI encoding, SHA256/MD5 hex, base64, HMAC-SHA256, curl trace logging, S3 Signature V4 headers, Swift headers, range headers, curl read/write/seek callbacks, and queue execution.

Control flow: Setup allocates `http_data`, initializes a CURL handle, configures verbosity, protocols, TLS verification policy, callbacks, optional basic auth, stores state, and forces thread mode. Queue builds an object path either per block (`file_offset_len`) or per file with optional HTTP `Range`. It sets URL, stream state, and upload size; adds S3 or Swift auth headers; then performs PUT for writes, GET for reads, and DELETE for trims. Status codes are mapped to success for expected ranges; missing read objects produce zero-filled buffers; other failures set `EIO`.

State/persistence: Per-thread state is one reusable CURL easy handle. Per-request state is stack-local stream and header list. Remote objects persist according to PUT/DELETE operations.

Dependencies/integration: Requires libcurl, OpenSSL HMAC/SHA/MD5, fio option parsing, diskless sync engine semantics, and server-specific S3/Swift/WebDAV behavior.

Risks: `_add_aws_auth_header()` and `_add_swift_header()` receive `slist` by value; appended header list is not returned to `fio_http_queue()`, so the local `slist` freed at exit may remain null and the CURL handle may retain/freeze header ownership incorrectly. Swift read/trim call `_add_swift_header()` with `dsha == NULL` but format it with `%s`, which is undefined. Fixed-size canonical request buffers can truncate long paths/tokens. S3 signing includes storage class for all methods, which may not match every S3-compatible service. TLS insecure mode disables both peer and host checks.

Test signals: Tests should cover WebDAV PUT/GET/DELETE, S3 SigV4 canonical output against known vectors, SSE-C headers, Swift write/read/trim, range reads near EOF, 404 zero-fill, TLS modes, and leak/error checks around repeated header lists.
