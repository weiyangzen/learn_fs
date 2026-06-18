# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_helpers.rs

## Purpose

This file provides shared SFTP e2e utilities: permissive host-key verification for ephemeral test servers, host-key generation, RustFS child-process cleanup, russh SFTP connection setup, full-file SFTP reads, S3 client construction, and S3 readiness polling.

## Important APIs, Types, And Functions

`AcceptAnyServerKey` implements `russh::client::Handler` and always accepts the server key. This is scoped to tests because each RustFS process generates a fresh host key and the suite exercises authentication and protocol behavior rather than host-key trust.

`generate_host_key(host_key_dir)` creates an ed25519 key pair in OpenSSH format using `russh::keys`, writes private and public files, and on Unix forces both to mode `0600`. The comment explains that the RustFS config loader scans every entry and rejects insecure permissions.

`ServerProcess` wraps `tokio::process::Child` in an `Option`. `kill_and_wait` asynchronously kills and reaps the child and is idempotent. `Drop` calls `start_kill` synchronously if the async cleanup path was skipped, preventing leaked RustFS listeners after panics.

`connect_sftp_to(address)` creates a russh client with `AcceptAnyServerKey`, authenticates with `DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY`, opens a session channel, requests the `sftp` subsystem, and returns both the russh handle and `SftpSession`. Returning the handle is required to keep the SSH transport alive for the SFTP session.

`sftp_read_full` opens a file with `OpenFlags::READ`, reads it into a `Vec<u8>`, then shuts down the handle. `build_test_s3_client(endpoint_url)` constructs an AWS SDK S3 client with default test credentials, us-east-1, path-style addressing, and an HTTP client override for `http://` endpoints. `wait_for_s3_ready` polls `ListBuckets` until it succeeds or the attempt budget expires.

## Control Flow

The helper flow is intentionally simple and reusable. Tests create an environment, call `generate_host_key`, spawn RustFS, wait for ports, call `connect_sftp_to`, then use SFTP and S3 helpers for assertions. Cleanup is either explicit through `ServerProcess::kill_and_wait` or panic-path best effort through `Drop`.

## State And Persistence Behavior

The only durable files this helper writes are ephemeral host-key files inside the per-test temp directory. It also controls child-process state and prevents leaked listeners. S3 and SFTP helpers do not maintain caches; they create fresh clients and sessions.

## Dependencies And Integration Points

This file depends on `russh`, `russh_sftp`, `aws_sdk_s3`, `aws_smithy_http_client`, `tokio`, `anyhow`, and test credential constants from `test_env.rs`. It is used by SFTP core and compliance tests and indirectly by the protocol runner. It bridges RustFS test credentials to both SFTP password auth and S3 signed client calls.

## Risks And Edge Cases

The host-key handler is intentionally insecure and must remain test-only. `ServerProcess::Drop` cannot await `wait`, so panic cleanup may leave a zombie until the runtime or parent process reaps it, but it still releases the listening port. `sftp_read_full` reads the whole object into memory and is not appropriate for multi-GiB fixtures; the compliance file uses streaming SHA256 for those cases. `wait_for_s3_ready` treats any successful `ListBuckets` as readiness and does not validate bucket-specific state.

## Test Signals

There are no direct unit tests in this file, but nearly all SFTP e2e tests depend on these helpers. Failures in key generation, permissions, auth, subsystem negotiation, child cleanup, S3 client config, or readiness polling surface quickly in SFTP core and compliance suites.
