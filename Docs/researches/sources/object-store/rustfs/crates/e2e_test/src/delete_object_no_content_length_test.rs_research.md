# sources/object-store/rustfs/crates/e2e_test/src/delete_object_no_content_length_test.rs

## Purpose
This regression test verifies that a signed raw `DELETE Object?versionId` request with no request body and no `Content-Length` header succeeds. It protects against regressions returning `MissingContentLength` for valid empty DELETE requests.

## Important APIs, Types, and Functions
`signed_delete_without_content_length` constructs a SigV4-signed HTTP DELETE request with `UNSIGNED_PAYLOAD`, manually omits any `Content-Length`, writes raw bytes to a `TcpStream`, and reads the raw response with a timeout. Helpers parse status and body from raw HTTP text.

## Control Flow
The test starts RustFS, creates a bucket, uploads an object, enables versioning, lists versions to obtain the version id, sends the raw signed DELETE for that version, asserts HTTP 204 and empty body, then verifies the explicitly deleted version is no longer readable.

## State and Persistence
State includes a versioned bucket, a pre-versioning object version, the version id, and the delete operation that removes that specific version. Raw network state is controlled through a manually opened TCP stream.

## Dependencies and Integration Points
The test integrates S3 versioning, list-object-versions, raw HTTP parsing, SigV4 signing, request-body handling, and DeleteObject version semantics.

## Risks and Edge Cases
The raw response parser is intentionally simple and assumes a complete response after connection close. The test focuses on DELETE with version id; unversioned deletes or delete-marker creation without Content-Length are not separately covered here.

## Test Signals
Signals include raw request validation that no `Content-Length` header is present, HTTP 204 response, absence of `MissingContentLength`, empty response body, and failure to GET the deleted version id.
