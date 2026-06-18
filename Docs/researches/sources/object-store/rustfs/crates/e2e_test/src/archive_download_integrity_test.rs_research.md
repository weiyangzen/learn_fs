# sources/object-store/rustfs/crates/e2e_test/src/archive_download_integrity_test.rs

## Purpose
This file provides archive-content integrity and content-encoding regression coverage for ZIP uploads and downloads, including multipart archives, SigV4 presigned downloads, reverse proxy forwarding, HTTP response compression interaction, and strict rejection of unsafe archive `Content-Encoding`.

## Important APIs, Types, and Functions
Helpers build stored ZIP bytes with `zip::ZipWriter`, generate deterministic random bytes, start RustFS with environment overrides, make signed PUT/GET requests with `rustfs_signer`, pre-sign GET URLs, and run a one-shot reverse proxy over `tokio::net::TcpListener`. `complete_archive_multipart_upload_with_content_encoding` creates a multipart ZIP object and returns the exact expected bytes. `assert_archive_object_content_encoding` checks HEAD, GET, and body equality.

## Control Flow
Tests start RustFS in different env modes, create buckets, upload ZIP objects by signed raw PUT or AWS SDK multipart APIs, then assert status codes, metadata, and exact bytes. Strict mode is toggled by `RUSTFS_REJECT_ARCHIVE_CONTENT_ENCODING`. HTTP compression is toggled with `RUSTFS_COMPRESS_ENABLE`, MIME type, and minimum-size variables. Presigned tests compare direct and proxied downloads against the original multipart ZIP bytes.

## State and Persistence
State includes temporary server data, buckets for regular and multipart archive tests, multipart upload ids and parts, content-encoding metadata, and generated archive bytes. The reverse proxy is transient and serves a single forwarded request.

## Dependencies and Integration Points
The file exercises S3 PutObject, CreateMultipartUpload, UploadPart, CompleteMultipartUpload, GetObject, HeadObject, conditional headers, SigV4 signing, presigned URLs, reqwest decompression controls, response compression configuration, and RustFS archive/content-encoding policy.

## Risks and Edge Cases
The tests are relatively expensive because they spawn servers and upload multi-megabyte data. They rely on fixed 5 MiB multipart thresholds and exact content-length behavior. Strict-mode behavior is archive-specific and tests ZIP content type rather than all archive MIME variants. Raw reverse proxy code is deliberately minimal and intended for a one-request path only.

## Test Signals
Signals include allowing normal archive content encoding by default, rejecting effective archive encodings in strict mode, stripping `aws-chunked` while preserving effective encodings, disabling HTTP compression for archive downloads, exact SHA-256/body equality for multipart downloads, ignoring empty conditional ETag headers, and preserving bytes through presigned direct and reverse-proxied downloads.
