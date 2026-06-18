# sources/object-store/rustfs/crates/e2e_test/src/content_encoding_test.rs

## Purpose
This suite verifies S3 `Content-Encoding` metadata handling. It ensures normal encodings round-trip through PUT/GET/HEAD, and SigV4 streaming marker `aws-chunked` is stripped rather than persisted.

## Important APIs, Types, and Functions
The tests use `RustFSTestEnvironment`, AWS SDK `ByteStream`, and S3 `put_object`, `get_object`, and `head_object`. There are no custom helpers beyond logging and environment setup.

## Control Flow
The first test uploads text with `content_type("text/plain")` and `content_encoding("zstd")`, then asserts GET and HEAD both return `zstd` and the original content. The second uploads with `content_encoding("aws-chunked")` and asserts GET and HEAD return no content encoding. The third uploads with `content_encoding("aws-chunked,gzip")` and asserts only `gzip` is returned by GET and HEAD.

## State and Persistence
Each test creates a fresh server, bucket, object, and content-encoding metadata. Metadata normalization is persisted by the server and observed through GET/HEAD.

## Dependencies and Integration Points
The file integrates AWS SDK metadata fields, RustFS upload metadata normalization, S3 response metadata reporting, and issue-specific handling for SigV4 streaming uploads.

## Risks and Edge Cases
Only a few encoding values are tested. The parser behavior for whitespace, multiple effective encodings, case differences, and malformed encodings is not covered here. The tests use AWS SDK upload calls, not raw chunked streaming bodies.

## Test Signals
Signals include exact `zstd` roundtrip, `aws-chunked` being absent in GET/HEAD, `aws-chunked,gzip` becoming exactly `gzip`, and body integrity after metadata normalization.
