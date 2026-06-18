# sources/object-store/rustfs/crates/ecstore/src/client/api_bucket_policy.rs

## Purpose
Implements transition-client bucket policy operations: set, put, remove, and get policy through S3-compatible `?policy` requests.

## Important APIs, Types, and Functions
- `set_bucket_policy` deletes the policy when passed an empty string, otherwise delegates to `put_bucket_policy`.
- `put_bucket_policy` sends `PUT` with `?policy`, policy bytes as body, and content length set to policy length; success is `204 No Content` or `200 OK`.
- `remove_bucket_policy` sends `DELETE ?policy` with an empty SHA256 hash and expects `204 No Content`.
- `get_bucket_policy` delegates to `get_bucket_policy_inner`.
- `get_bucket_policy_inner` sends `GET ?policy`, buffers the full body, and returns it as lossy UTF-8.

## Control Flow and State Behavior
Every method builds `RequestMetadata` for `TransitionClient::execute_method`. Error responses are converted with `http_resp_to_error_response`, but `get_bucket_policy_inner` does not check status before returning the body.

## Dependencies and Integration Points
Uses `TransitionClient`, `RequestMetadata`, `ReaderImpl`, `http`, `hyper::Bytes`, `http_body_util::BodyExt`, `HeaderMap`, and `EMPTY_STRING_SHA256_HASH`. It is part of the client API surface for bucket policy migration/transition operations.

## Persistence
The client does not persist locally. Successful requests mutate bucket policy on the remote endpoint.

## Risks and Edge Cases
`get_bucket_policy_inner` ignores non-OK statuses and may return an XML error body as a policy string. Bodies are fully buffered without using `MAX_S3_CLIENT_RESPONSE_SIZE` despite importing it. Empty policy as delete is convenient but prevents setting a deliberately empty policy document if such a thing were ever meaningful.

## Test Signals
No inline tests. Tests should cover status handling, non-UTF-8 body behavior, empty policy delete behavior, and response body limits.
