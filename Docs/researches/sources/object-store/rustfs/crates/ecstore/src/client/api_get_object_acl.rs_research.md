# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_acl.rs

## Purpose
Implements `GET ?acl` for an object and maps returned ACL grants into object metadata, especially canned ACL headers.

## Important APIs, Types, and Functions
- DTOs: `Grantee`, `Grant`, `AccessControlList`, and `AccessControlPolicy`.
- `TransitionClient::get_object_acl` sends `GET` with `acl` query, buffers the body, converts non-OK responses through `http_resp_to_error_response`, parses XML ACL, fetches `stat_object`, copies owner fields, and inserts `X-Amz-Acl` for recognized canned ACLs.
- `get_canned_acl` detects `private`, `authenticated-read`, `public-read`, `bucket-owner-read`, and `public-read-write` from grant patterns.
- `get_amz_grant_acl` maps grant permissions to `X-Amz-Grant-*` header value lists.

## Control Flow and State Behavior
The method fetches ACL first, then fetches object stat and enriches the returned `ObjectInfo`. Grant-header mapping is computed but currently not inserted because that loop is commented out.

## Dependencies and Integration Points
Depends on `TransitionClient`, `GetObjectOptions`, `ObjectInfo`, request metadata, `http_body_util`, `quick_xml`, S3 `Owner`, and `http` headers. It integrates ACL results with object stat metadata.

## Persistence
No local persistence. It reads remote ACL state.

## Risks and Edge Cases
`AccessControlPolicy.owner` is marked `serde(skip)`, so parsed owner fields will remain default; copying owner into `obj_info` is likely ineffective. `get_canned_acl` calls `ac_policy.owner.id.clone().unwrap()` and can panic if owner ID is absent in the two-grant bucket-owner-read case. Full grant ACL headers are computed but discarded. XML parsing uses `String::from_utf8(...).unwrap()`, so invalid UTF-8 panics.

## Test Signals
No inline tests. Tests should cover XML owner parsing, canned ACL detection, grant header insertion, malformed UTF-8/XML, and non-OK error conversion.
