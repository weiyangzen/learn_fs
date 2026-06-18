# sources/object-store/rustfs/crates/e2e_test/src/protocols/ftps_core.rs

Purpose: core FTPS E2E test for RustFS protocol support. It starts RustFS with FTPS enabled, connects with a TLS-capable FTP client, and verifies bucket/object operations through FTPS map correctly to object-store semantics.

Important APIs/types/functions: constants `FTPS_PORT` and `FTPS_ADDRESS` fix the test endpoint. `AcceptAnyServerCertVerifier` implements rustls certificate and signature verification by accepting all certs for generated self-signed test certificates. `test_ftps_core_operations` is the exported async entry point. It generates default and domain-specific cert/key pairs with `rcgen`, starts RustFS via `tokio::process::Command`, builds a dangerous rustls client config, and uses `suppaftp::RustlsFtpStream` for FTP commands.

Control flow: create protocol temp environment and cert directory, write self-signed certificates, spawn RustFS with `RUSTFS_FTPS_ENABLE`, `RUSTFS_FTPS_ADDRESS`, and `RUSTFS_FTPS_CERTS_DIR`, wait for port readiness, install the aws-lc rustls provider, connect and upgrade to TLS, login with default credentials, then run a command walkthrough: `mkdir` bucket, `cwd`, upload, download and compare content, list relative/root/absolute paths, `cwd .`, `cwd /`, delete object, reject cwd to nonexistent bucket, remove bucket, verify final listing, and quit. The server process is killed and waited after the async test body completes.

State and persistence behavior: creates a temporary RustFS data directory and certificate files. FTPS operations create a bucket and object, then delete both before exit. The spawned RustFS process is manually owned by this test and killed on completion.

Dependencies and integration points: uses `ProtocolTestEnvironment`, shared binary resolution with features `ftps,webdav`, rustls/aws-lc, `rcgen`, `suppaftp`, default protocol credentials, and the RustFS FTPS listener. The test bridges FTP verbs to S3-like bucket/object behavior.

Risks: fixed port 9021 can conflict with other local runs. Accept-all certificate verification is correct for local generated certs but must remain test-only. `install_default` for the rustls crypto provider is global and can only succeed once per process, depending on rustls behavior. The test uses blocking suppaftp operations inside an async function, which is acceptable for E2E but can occupy a Tokio worker.

Test signals: validates FTPS TLS startup, authentication, bucket creation/removal, object upload/download/delete, path normalization for root/current/absolute paths, directory listings, and error handling for nonexistent buckets.
