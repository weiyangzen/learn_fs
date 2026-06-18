# sources/object-store/rustfs/crates/protocols/src/swift/handler.rs

## Purpose
`handler.rs` is the Swift HTTP integration layer. It wraps an underlying S3 Tower service, recognizes Swift routes, retrieves Keystone credentials, handles TempURL bypasses, dispatches account/container/object operations, and falls back to S3 for non-Swift requests.

## Important APIs, Types, And Functions
`SwiftService<S>` owns a `SwiftRouter` and fallback S3 service and implements `tower::Service`. `handle_swift_request` performs TempURL detection and normal authentication. `handle_authenticated_request` is the main route dispatcher. Helper functions include `handle_tempurl_object_request`, symlink resolution, `handle_object_get`, `handle_object_head`, `handle_object_put`, `check_container_acl`, a local `parse_range_header`, CORS injection, `swift_error_to_response`, and `generate_trans_id`.

## Control Flow
Request flow is route match, credential extraction from `KEYSTONE_CREDENTIALS`, body normalization to `s3s::Body`, optional TempURL validation for object GET/HEAD/PUT, then authenticated dispatch. Account routes list containers, update account metadata, and support bulk delete. Container routes create/delete containers, list objects with query filters, return metadata/ACL/versioning headers, update metadata/ACL/versioning, handle bulk extract, FormPost, and CORS preflight. Object routes enforce ACLs, handle SLO/DLO/versioning/staticweb/symlink paths, stream regular PUT/GET/HEAD/POST/DELETE, and support COPY.

## State, Persistence, And Dependencies
The handler persists no state directly. It coordinates durable state through account, container, object, ACL, CORS, DLO/SLO, versioning, staticweb, symlink, tempurl, bulk, quota, and formpost modules. It depends on Tower, Axum HTTP types, Tokio stream readers, Keystone task-local credentials, and RustFS body wrappers.

## Integration Points
This file is the only listed module that actively wires DLO, FormPost, quota, expiration metadata through object PUT, symlink resolution, CORS, and versioning. It does not wire `encryption.rs` or `ratelimit.rs`. TempURL detection calls account TempURL key lookup before requiring normal auth, but helper object access still fails when credentials are absent.

## Risks And Test Signals
The dispatcher is large and contains duplicated regular object GET logic and duplicated range parsing. Handler-local `swift_error_to_response` drops special `TooManyRequests` headers from `errors.rs`. TempURL GET/HEAD/PUT currently routes to helpers that return "not fully implemented" without credentials, despite successful TempURL signature validation. Some headers are parsed case-sensitively by string prefix checks even though HTTP headers are case-insensitive. Tests only cover handler-local range parsing; route dispatch, TempURL, ACLs, CORS, DLO/SLO, copy, and versioning need integration tests.
