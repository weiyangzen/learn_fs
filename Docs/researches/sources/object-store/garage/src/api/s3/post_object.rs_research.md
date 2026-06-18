# sources/object-store/garage/src/api/s3/post_object.rs

## Purpose
Implements browser-based S3 POST object upload using multipart/form-data policies. It verifies the signed policy, validates form fields and content length constraints, then delegates object writing to the normal `save_stream` PUT path.

## Important APIs, Types, And Functions
`handle_post_object` is the entry point. `Policy`, `PolicyCondition`, `Conditions`, and `Operation` model the base64 JSON policy document. `StreamLimiter` enforces `content-length-range` while streaming the file. The function also handles `${filename}` substitution, CORS response headers, success redirects, and `success_action_status`.

## Control Flow
The handler extracts the multipart boundary, applies size constraints, reads form fields until the `file` part, and stores prior fields in a `HeaderMap` while rejecting duplicate names. It validates required `key` and `policy`, parses form authorization, substitutes filename if requested, verifies SigV4 over the policy, resolves the bucket, checks write permission, and computes matching CORS rule before upload. It decodes and validates policy expiration and conditions, consumes each provided form field against the allowed condition set, rejects missing required policy fields, extracts metadata/checksum/encryption settings, and streams the file through `save_stream` with checksum verification and length limiting.

## State And Persistence
Persistent object state is created entirely by `save_stream`: object table, version table, block refs, block storage, and quota checks. This file stores no policy state. It influences metadata headers, checksum metadata, object encryption, and response behavior.

## Dependencies And Integration Points
Depends on `multer` for multipart parsing, SigV4 form verification from `garage_api_common::signature::payload`, CORS helpers, shared checksum parsing, `put::save_stream`, and encryption derivation. It constructs a `ReqCtx` after policy authorization and bucket resolution.

## Risks And Test Signals
Risks include policy-condition parity with AWS, form field normalization, rejecting or accepting `x-ignore-*`, and streaming length enforcement only becoming final at EOF for undersized files. Success location construction assumes HTTPS when a host is present. Unit tests cover policy condition deserialization and normalization; they do not cover authorization, multipart parsing, CORS, upload persistence, or success responses.
