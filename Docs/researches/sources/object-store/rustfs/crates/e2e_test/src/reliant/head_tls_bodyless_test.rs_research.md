# sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs

Purpose: regression coverage for wire-level `HEAD` responses over TLS/HTTP2. It verifies missing-object `HEAD` returns `404` with no body bytes, preventing HTTP/2 DATA frames after headers that clients report as protocol errors.

Important APIs and functions: `generate_tls_bundle` writes self-signed cert/key files into the test TLS directory. `local_https_h2_client` creates a reqwest client with compression disabled and invalid certs accepted. `signed_empty_request` constructs an HTTP request, signs it with RustFS SigV4 using `UNSIGNED_PAYLOAD`, and sends it through reqwest. `ensure_bucket_exists` uses signed `HEAD` and `PUT` bucket requests. `wait_for_tls_server_ready` polls the root endpoint. `start_tls_rustfs_server` launches the RustFS binary with `RUSTFS_TLS_PATH` and explicit address/credentials.

Control flow: the test creates a temporary `RustFSTestEnvironment`, generates TLS material, starts RustFS as HTTPS, waits for readiness, ensures the bucket exists, then performs a signed `GET` and signed `HEAD` for the same missing object. The `GET` path must return `404` with an XML body containing `NoSuchKey` or `NoSuchObject`. The `HEAD` path must return `404`, use HTTP/2, and yield an empty byte body.

State and persistence: state is confined to the temporary RustFS environment, temp storage, generated TLS files, and child process stored on the environment. No object is created for the missing key.

Dependencies and integration points: test harness common utilities, RustFS binary launch, rcgen, reqwest, HTTP/2, SigV4 signer, S3 body type, Tokio fs/time, and RustFS TLS configuration.

Risks: this is not ignored, but it requires a buildable RustFS binary and local process spawning. The client currently accepts invalid certs even though a CA PEM is produced. Readiness polling treats any successful root `GET` as ready, which depends on root endpoint behavior. It explicitly asserts HTTP/2 for `HEAD`, so client/server protocol negotiation changes can fail the test.

Test signals: compares `GET` error body behavior with `HEAD` bodylessness for the same missing object and validates the actual transport protocol version.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/head_tls_bodyless_test.rs -->
