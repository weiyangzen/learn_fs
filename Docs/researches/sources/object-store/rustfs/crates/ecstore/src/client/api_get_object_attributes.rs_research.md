# sources/object-store/rustfs/crates/ecstore/src/client/api_get_object_attributes.rs

## Purpose
Implements a client call for S3 `GetObjectAttributes`, including request option headers and response parsing into object attributes, checksum, and parts structures.

## Important APIs, Types, and Functions
- `ObjectAttributesOptions` carries `max_parts`, `version_id`, and `part_number_marker`.
- `ObjectAttributes` stores response version ID, last-modified time, and `ObjectAttributesResponse`.
- DTOs: `Checksum`, `ObjectParts`, `ObjectAttributesResponse`, and private `ObjectAttributePart`.
- `ObjectAttributes::parse_response` reads `Last-Modified`, `x-amz-version-id`, and XML body.
- `TransitionClient::get_object_attributes` builds `?attributes`, headers for requested attributes/max parts/part marker, sends a request, checks endpoint support, handles non-OK, and parses the response.

## Control Flow and State Behavior
The client uses `HEAD` with `?attributes` and `x-amz-object-attributes` headers, then reads the body. It treats a non-empty `ETag` header as evidence that the endpoint does not support object attributes and returns an unsupported error. Non-OK bodies are parsed as `AccessControlPolicy` and return its permission field as an error.

## Dependencies and Integration Points
Depends on constants such as `GET_OBJECT_ATTRIBUTES_MAX_PARTS`, S3 attribute headers, `TransitionClient`, request metadata, `quick_xml`, `time`, and `AccessControlPolicy` from the ACL module.

## Persistence
No local persistence. It reads remote object metadata.

## Risks and Edge Cases
Many header reads use `unwrap`, so missing `ETag`, `Last-Modified`, or version ID can panic. The use of `HEAD` while expecting a body is suspicious for S3 `GetObjectAttributes`, which is normally a `GET` operation. The endpoint-support check appears inverted or brittle: a normal object `ETag` header causes unsupported. Non-OK error parsing as ACL policy is likely wrong. Imported response-size limits are not enforced.

## Test Signals
No inline tests. Tests should cover supported and unsupported endpoint responses, missing headers, versionless objects, XML body parsing, non-OK S3 error parsing, and correct HTTP method expectations.
