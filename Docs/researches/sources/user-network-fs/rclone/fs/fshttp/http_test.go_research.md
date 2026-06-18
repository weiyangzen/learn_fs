# sources/user-network-fs/rclone/fs/fshttp/http_test.go

## Purpose
`http_test.go` validates the security-sensitive and lifecycle-sensitive behavior in `fshttp/http.go`: header redaction for debug dumps/curl commands and client TLS certificate reloading when cert files change.

## Important APIs, types, and functions
The tests exercise unexported helpers `cleanAuth`, `cleanAuths`, `cleanCurl`, the package `expireWindow`, and public `NewClient`. Local helpers `createTestCert` and `writeTestCert` generate short-lived self-signed RSA client certificates, and `TestCertificates` uses `httptest.NewTLSServer` with `tls.RequestClientCert`.

## Control flow
The redaction tests run table-driven strings through the scrubbers and assert that Authorization and X-Auth-Token values are replaced with `XXXX` without removing unrelated headers. `TestCertificates` starts a TLS server, configures rclone client cert/key paths, makes one request, waits for expiry, overwrites the cert/key with a new serial number, then makes another request through the same client to prove `RoundTrip` reloads expiring certs.

## State and persistence behavior
The certificate test writes temporary cert/key files and mutates the shared config returned by `fs.GetConfig(ctx)`. It relies on the package-level certificate expiry window and the `Transport`'s in-memory TLS config being updated after file replacement.

## Dependencies and integration points
The tests depend on Go crypto/x509, `httptest`, rclone `fs.ConfigInfo`, `NewClient`, and `http2curl`. They directly protect logging behavior used by HTTP dump flags and TLS behavior used by backends requiring mutual TLS.

## Risks and edge cases
The generated certificate validity is deliberately short, so test timing can be sensitive on very slow machines. `writeTestCert` accepts a validity parameter but currently calls `createTestCert(1 * time.Second)`, so the test depends on the constant behavior. Shared config mutation must not leak badly between tests.

## Test signals
Good coverage exists for auth redaction variants, both supported sensitive headers, curl command rewriting, cert reload through real TLS handshakes, and serial-number progression at the server side.

Source-read signal: reviewed complete local file (204 lines). Functions/methods observed: `TestCleanAuth`, `TestCleanAuths`, `TestCleanCurl`, `createTestCert`, `writeTestCert`, `TestCertificates`.
