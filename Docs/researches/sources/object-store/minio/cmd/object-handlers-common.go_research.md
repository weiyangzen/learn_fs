# sources/object-store/minio/cmd/object-handlers-common.go

## Purpose
This file contains shared HTTP object-handler helpers for conditional request evaluation, ETag normalization, common PUT/COPY/DELETE response headers, and lifecycle-driven batched object version deletion. It centralizes S3 precondition semantics used by GET, HEAD, PUT, CopyObject, and CopyObjectPart handlers.

## Important APIs, types, and functions
- `checkCopyObjectPartPreconditions` delegates to `checkCopyObjectPreconditions`.
- `checkCopyObjectPreconditions` evaluates `x-amz-copy-source-if-*` headers for CopyObject and CopyObjectPart PUT requests.
- `checkPreconditionsPUT` evaluates PUT `If-Match`, `If-None-Match`, and MinIO preserve-ETag/version safeguards.
- `writeHeadersPrecondition` writes common object metadata headers for 304 and 412 responses.
- `checkPreconditions` evaluates GET/HEAD `If-*` headers and part-number validity.
- `ifModifiedSince` performs S3-compatible one-second timestamp precision comparison.
- `canonicalizeETag` and `isETagEqual` normalize quoted ETags and wildcard matching.
- `setPutObjHeaders` writes success headers for PUT/COPY/complete multipart/delete, including version IDs, delete-marker state, lifecycle prediction headers, and checksums.
- `deleteObjectVersions` deletes lifecycle-selected object versions in batches and emits lifecycle audit/events.

## Control flow
Copy preconditions only run for PUT. They skip modtime conditions if object modification time is zero or Unix epoch, write common headers before failure responses, and map failed copy-source conditions to `ErrPreconditionFailed`.

GET/HEAD preconditions first reject invalid requested part numbers when `opts.PartNumber > 1`. They then apply S3 precedence: matching `If-None-Match` returns `304 Not Modified` before considering `If-Modified-Since`; stale `If-Modified-Since` also returns 304; failing `If-Match` returns 412; `If-Unmodified-Since` returns 412 only when `If-Match` is absent. `writeHeadersPrecondition` preserves metadata such as version ID, expiry, and cache-control on conditional responses.

PUT preconditions skip non-PUT/POST methods, zero/epoch modtimes, and delete markers. They fail on mismatched `If-Match`, matching `If-None-Match`, or an exact match of `opts.PreserveETag` and `opts.VersionID`, preventing redundant or conflicting writes.

`deleteObjectVersions` chunks lifecycle deletes by `maxDeleteList`, reads bucket versioning state, calls `ObjectLayer.DeleteObjects`, emits lifecycle audit logs, and sends delete events with per-object error response details when necessary.

## State and persistence behavior
Precondition helpers do not mutate object storage, but they write response headers and status codes, and their boolean return value controls whether handlers proceed to read or write persistent object data. `setPutObjHeaders` exposes persisted object state such as ETag, version ID, delete-marker flag, lifecycle predictions, and decrypted checksums. `deleteObjectVersions` directly mutates storage by deleting object versions through `ObjectLayer.DeleteObjects`.

## Dependencies and integration points
The helpers depend on `ObjectInfo`, `ObjectOptions`, MinIO error mapping, HTTP constants, lifecycle and event systems, object versioning configuration, checksum decryption, and audit logging. `object-handlers.go` uses these functions in GET, HEAD, PUT, COPY, DELETE, object lock, and metadata update paths.

## Risks and edge cases
S3 conditional precedence is subtle; reordering checks can change compatibility. Timestamp comparison intentionally rounds with `givenTime.Add(1 * time.Second)` to account for HTTP date precision. `isETagEqual` treats right-side `*` as wildcard, which is correct for headers but should not be reused for arbitrary ETag equality without considering that behavior. `deleteObjectVersions` assumes `lcEvent` aligns with `toDel` indexes across batching.

## Test signals
The paired test file covers ETag canonicalization and important `If-None-Match`/`If-Modified-Since` plus `If-Match`/`If-Unmodified-Since` precedence. Copy-source preconditions, PUT preconditions, response checksum headers, and lifecycle deletion batching are not directly tested here.
