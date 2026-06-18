# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_core.rs

## Purpose

This file defines core SFTP e2e tests for RustFS. It verifies the basic SFTP surface against a spawned RustFS binary, then checks cross-protocol consistency between SFTP and the same server's S3 endpoint. A second public function verifies idle-timeout disconnect behavior on dedicated ports.

## Important APIs, Types, And Functions

`connect_sftp()` is a tiny wrapper around `connect_sftp_to(SFTP_ADDRESS)`. `assert_cross_protocol_sha_match` is the key reusable assertion: it computes an expected SHA256, reads the object through S3 `GetObject`, reads the same object through SFTP via `sftp_read_full`, and verifies both length and digest.

`test_sftp_core_operations()` is the main exported async test body. It generates a host key, spawns RustFS with SFTP enabled, read-only disabled, `ENV_SFTP_PART_SIZE` pinned to 5 MiB, and the S3 address on port 9200. It exercises subsystem negotiation, bucket mkdir/listing, small file write/read, stat, setstat, rename, multipart-sized write/read, negative SFTP operations, bad password handling, cross-protocol SFTP-to-S3 and S3-to-SFTP byte identity, directory marker visibility, and cleanup.

`test_sftp_idle_timeout_disconnects()` spawns a separate RustFS process on SFTP port 9023 and S3 port 9100, sets `ENV_SFTP_IDLE_TIMEOUT` to 5 seconds, confirms the session is live, sleeps 10 seconds, and expects the next SFTP request to fail.

## Control Flow

Both public functions follow a similar pattern: create `ProtocolTestEnvironment`, generate host keys, spawn RustFS with feature-gated binary path, wait for the SFTP port, connect using the shared russh helper, run assertions inside an async block, then kill and wait for the child with `ServerProcess`.

The main core flow starts with a canary `canonicalize(".")`, creates a bucket through SFTP `create_dir`, lists root, writes `small.txt`, reads it back, compares SHA256, stats file and bucket, performs no-op SETSTAT, renames to `renamed.txt`, and lists to confirm the old name is gone. It then writes a deterministic `MULTIPART_SIZE` buffer just over two 5 MiB parts and checks the multipart round trip. Negative cases assert errors for symlink, nonexistent open, nonexistent directory listing, traversal, append, create-exclude on an existing key, write-only open, write-create without truncate, and bad password auth.

After S3 readiness, cross-protocol checks write through SFTP and read through both protocols, then write through S3 and read through both protocols. Directory visibility checks ensure SFTP-created directories are visible to S3 listing and S3-created `__XLDIR__` markers are decoded as SFTP directories.

## State And Persistence Behavior

The test creates and removes real buckets, files, and directory markers in the spawned RustFS data directory. Payloads are deterministic so byte corruption is caught by SHA256. The multipart branch is made deterministic by pinning `ENV_SFTP_PART_SIZE` and using `MULTIPART_SIZE = part_size * 2 + 1024`.

The file repeats `XLDIR_SUFFIX` locally because this e2e crate does not depend on `rustfs-utils`. That suffix is part of the persistence contract between S3 object keys and SFTP directory views.

## Dependencies And Integration Points

The file integrates local helpers from `sftp_helpers.rs` and `test_env.rs`, RustFS config constants, `aws_sdk_s3`, `russh`, `russh_sftp`, `tokio`, and `sha2`. `test_runner.rs` schedules `test_sftp_core_operations` and `test_sftp_idle_timeout_disconnects` when the `sftp` feature is requested. The spawned binary path comes from `rustfs_binary_path_with_features(Some("ftps,webdav,sftp"))`.

## Risks And Edge Cases

Fixed ports 9022/9200 and 9023/9100 can conflict with other local processes. The cross-protocol section requires both SFTP and S3 stacks to be healthy in the same RustFS process; port readiness alone is not enough, so `wait_for_s3_ready` is used. Some negative assertions only check `is_err`, not exact status codes, which is robust to client error type changes but less precise for protocol-status regressions.

## Test Signals

Signals include SFTP session negotiation, root and bucket listings, file stat metadata, SHA256 checks for small and multipart payloads, unsupported operation errors, auth failure, S3/SFTP byte identity in both write directions, directory marker interoperability, and post-timeout request failure.
