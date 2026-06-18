# sources/object-store/openstack-swift/swift/common/middleware/s3api/controllers/multi_delete.py

Purpose: Implements S3 Delete Multiple Objects by parsing an XML delete request and issuing concurrent Swift object deletes.

Important APIs and control flow: `MultiObjectDeleteController.POST` is public and bucket-scoped. It bounds request-body size by configured max objects and object-name length, requires a body and Content-MD5, validates `Delete` XML, parses `Quiet`, and builds `(key, version)` pairs. It HEADs the bucket, returns per-key AccessDenied XML if the bucket check fails, and rejects non-null version IDs unless Swift object versioning is available. `do_delete` shallow-copies the request, sets `object_name`, handles version queries, asks the request for multipart manifest delete query data, deletes with `Accept: application/json`, parses synchronous SLO bulk-delete responses, and converts `NoSuchKey` to success. `StreamingPile` runs deletes with configured concurrency and the response XML includes either `Error` elements or, unless quiet, `Deleted` elements.

State, dependencies, and integration: Persistent changes are Swift object deletes and optional SLO segment cleanup. It depends on object versioning feature registration, multipart delete helpers, and the concurrency utility.

Risks and test signals: Error aggregation must preserve S3 semantics while Swift bulk delete has different response formats. Tests should cover missing body, bad XML, max-object limits, quiet mode, AccessDenied bucket HEAD, versioning unavailable, SLO delete errors, concurrent partial failures, and request-copy isolation.
