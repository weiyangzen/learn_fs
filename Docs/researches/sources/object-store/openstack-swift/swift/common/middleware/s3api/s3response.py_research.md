<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py -->
# sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py

## Purpose
Defines the S3 response layer for `s3api`: normal response header normalization, Swift-to-S3 header translation, SLO/multipart ETag presentation, copy response bodies, and a large catalog of XML-formatted S3 error responses.

## Important APIs, types, and functions
`HeaderKeyDict` preserves S3 casing expectations, notably `ETag` and lowercase `x-amz-*`. `translate_swift_to_s3(key, val)` converts Swift object/container headers into S3-compatible headers and drops internal-only headers. `S3Response` wraps `swob.Response`, extracts S3 sysmeta, handles legacy `swift3` sysmeta, records `sw_headers` and `sysmeta_headers`, and exposes `from_swift_resp`. `append_copy_resp_body` emits `CopyObjectResult`/`CopyPartResult` XML. `ErrorResponse` serializes S3 error XML and produces metric names; subclasses encode specific S3 status/code/message combinations.

## Control flow
On response construction, all incoming headers are split into S3 sysmeta and ordinary Swift headers. Ordinary headers are translated, sysmeta can override multipart ETag, and SLO responses without stored AWS-style ETags get a `-N` suffix to discourage client-side validation assumptions. Errors lazily generate XML bodies in `_body_iter`, adding `RequestId` after WSGI environ is available, then render nested info dictionaries as XML tags.

## State and persistence behavior
`S3Response` stores translated public headers, raw Swift headers, and S3 sysmeta headers for later ACL and multipart decisions. It does not persist data itself, but it interprets persisted sysmeta such as `x-object-sysmeta-s3api-etag` and old `swift3` keys. `ErrorResponse` stores per-instance `_msg`, `reason`, and structured `info` used for response bodies and metrics.

## Dependencies and integration points
Used by `s3request` and all S3 controllers as the common response/error vocabulary. It depends on Swift header utilities, `is_sys_meta`, S3 XML helpers, S3 utility naming functions, server-side encryption cipher conversion, and object-versioning delete-marker content type. It is also the bridge that exposes SLO/multipart fields as `x-amz-mp-parts-count`, `x-amz-version-id`, `x-amz-copy-source-version-id`, and delete-marker headers.

## Risks and test signals
Risks include leaking Swift/internal headers, incorrect casing for client SDKs, stale legacy sysmeta precedence, malformed XML from invalid info values, and mismatched SLO ETag semantics. Tests should assert header allow/drop behavior, user metadata underscore restoration, CORS header translation, expiration and encryption header translation, copy response XML, RequestId injection, metric names, and constructor behavior for error subclasses that require bucket/key/version arguments.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/s3api/s3response.py -->
