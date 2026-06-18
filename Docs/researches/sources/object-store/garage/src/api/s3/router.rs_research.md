# sources/object-store/garage/src/api/s3/router.rs

## Purpose
Maps HTTP method, bucket/key addressing, query parameters, and selected headers to typed S3 `Endpoint` variants, and assigns each endpoint an authorization class.

## Important APIs, Types, And Functions
`Endpoint` enumerates supported and stubbed S3 operations. `Endpoint::from_request` parses a request into `(Endpoint, Option<bucket>)`. Method-specific parsers `from_get`, `from_head`, `from_post`, `from_put`, and `from_delete` are generated with `router_match!`. `get_key` extracts object keys for key-based endpoints. `authorization_type` maps endpoints to `Authorization::{None, Read, Owner, Write}`. `generateQueryParameters!` declares recognized operation keywords and query fields.

## Control Flow
`from_request` handles root requests as `ListBuckets` or `Options`, derives bucket/key from either host-style bucket input or path-style URI, percent-decodes the key, parses query parameters, dispatches by HTTP method, warns when `x-id` does not match the parsed endpoint name, and logs unused query parameters. PUT routing gives copy operations precedence when `x-amz-copy-source` is present, distinguishing `CopyObject` from `UploadPartCopy` by `partNumber`.

## State And Persistence
No persistence. It creates the request classification that controls downstream authorization and handler selection.

## Dependencies And Integration Points
Depends on router macros from `garage_api_common`, Hyper request/header types, and the common `Authorization` enum. The API server consumes `Endpoint` to build `ReqCtx`, enforce permissions, and call the appropriate handler module.

## Risks And Test Signals
Risks are endpoint ambiguity, unsupported operations being parsed as typed variants but not implemented elsewhere, query parameter parsing mismatches, and authorization classification drift. The module has extensive tests based on AWS documentation examples, bucket/key extraction, percent decoding, invalid endpoints, copy header routing, upload-part-copy routing, and authorization type expectations. A commented failing plus-to-space case records an unresolved URL encoding question.
