# sources/object-store/rustfs/crates/e2e_test/src/protocols/webdav_core.rs

## Purpose

This file defines the core WebDAV e2e suite for RustFS. It starts a RustFS process with WebDAV enabled, exercises authenticated WebDAV collection and object operations, validates directory move behavior, checks authorization failure atomicity, and verifies failed authentication.

## Important APIs, Types, And Functions

`create_client()` builds a reqwest client accepting invalid certs, although this test disables WebDAV TLS. `basic_auth_header` and `basic_auth_header_for` build Basic auth headers from default or supplied credentials.

`signed_admin_request` builds and signs RustFS admin API requests with AWS Signature V4 using `rustfs_signer`. It sets `Host`, `x-amz-content-sha256: UNSIGNED-PAYLOAD`, optional content type, signs with default admin credentials, then sends through the local HTTP client. `admin_create_user`, `admin_add_canned_policy`, and `admin_attach_policy_to_user` wrap specific admin API endpoints and bail with response status/body on failure.

`test_webdav_core_operations()` is the main exported async test body. It spawns RustFS with `--address` for the S3/admin endpoint, `RUSTFS_WEBDAV_ENABLE=true`, `RUSTFS_WEBDAV_ADDRESS=127.0.0.1:9080`, and TLS disabled. The direct `#[tokio::test]` entry simply calls this function and is marked serial.

## Control Flow

The suite waits for the WebDAV port, creates a reqwest client and Basic auth header, then runs a sequential workflow. It starts with `PROPFIND` at root, `MKCOL` to create a bucket, `PUT`/`GET`/`PROPFIND` for a file, `DELETE` of that file, and a 404 check for the deleted object. It then tests file `MOVE` and verifies source deletion and destination content.

Directory behavior follows: `MKCOL` creates a directory, `PUT` writes inside it, `PROPFIND` lists it, `GET` on the collection is expected to return 405, `MOVE` renames the directory, and nested directory creation plus nested `MOVE` preserve contained file content.

The authorization regression creates a restricted bucket and source directory, writes a file, creates a limited user with `ListBucket`, `GetObject`, and `PutObject` but no `DeleteObject`, then attempts a directory `MOVE`. It asserts the move is rejected, no destination object is created, and the source remains byte-identical. Finally it deletes the main bucket and checks invalid Basic auth returns 401.

## State And Persistence Behavior

The test writes real buckets, objects, and directory-shaped prefixes into the spawned RustFS temp directory. MOVE operations are validated as copy/delete behavior from the WebDAV view, and the restricted MOVE check is specifically about atomicity: denied delete permission must not leave partial destination writes. Admin users and canned policy state are created through RustFS admin APIs within the same process.

## Dependencies And Integration Points

The file depends on `reqwest`, `base64`, `http`, `rustfs_signer`, `s3s::Body`, `serde_json`, `tokio`, and local common/test environment helpers. `test_runner.rs` schedules `test_webdav_core_operations` when the `webdav` feature is enabled. It uses `ProtocolTestEnvironment` only for temp storage and port readiness, while child process cleanup is handled directly with `kill` and `wait`.

## Risks And Edge Cases

The suite uses fixed WebDAV and S3/admin ports 9080 and 9010. It assumes admin API paths and SigV4 signing behavior stay compatible with the JSON payloads used here. Cleanup is focused on killing the process; not all created buckets/users/policies are explicitly removed before process teardown. Some status assertions accept several success codes to accommodate WebDAV variations, but exact failure cases are pinned for 404, 405, and 401.

## Test Signals

Signals include WebDAV status codes for `PROPFIND`, `MKCOL`, `PUT`, `GET`, `DELETE`, and `MOVE`; body content equality after GET and MOVE; PROPFIND response contents; collection GET returning 405; authorization-denied directory MOVE leaving no destination and preserving source; successful admin user/policy calls; and invalid auth returning 401.
