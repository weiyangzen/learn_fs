# sources/object-store/minio/cmd/api-headers.go

## Purpose
Builds common S3 response headers, XML/JSON encoders, event-stream headers, multipart part-count headers, and object metadata/range headers for object responses.

## Important APIs, types, and functions
- `mustGetRequestID` formats nanosecond timestamps as uppercase hex request ids.
- `setEventStreamHeaders` disables buffering for event streams.
- `setCommonHeaders` sets server, region, accept-ranges, and removes sensitive crypto headers.
- `encodeResponse`, `encodeResponseList`, and `encodeResponseJSON` serialize XML, control-character-safe list XML, and JSON.
- `setObjectHeaders` is the main object response header builder.
- `needsMimeEncoding` decides whether user metadata values require RFC 2047 encoding.

## Control flow
`setObjectHeaders` first applies common headers, last-modified, ETag, content type/encoding/expires, tag count, optional tag echoing, and user metadata. It filters internal/reserved metadata and the unencrypted length/MD5 headers from a security advisory. User metadata values with non-ASCII/control bytes are MIME encoded. It computes actual object size, derives range from explicit range or part number, sets content length/range, version and replication headers, transitioned storage class, lifecycle prediction headers, and compression metadata.

## State and persistence behavior
No persistent writes. It reads `globalSite.Region()` and `globalLifecycleSys`, and derives response state from `ObjectInfo`, `HTTPRangeSpec`, and `ObjectOptions`.

## Dependencies and integration points
Used by object GET/HEAD and listing paths. Integrates with crypto metadata filtering, object tags parsing, MinIO HTTP header constants, lifecycle prediction, multipart part metadata, and range helpers.

## Risks and edge cases
Header behavior is security-sensitive: leaking reserved metadata, unencrypted length/MD5, or incorrect SSE headers can expose internal state. Range/part-number conversion can return errors that must be propagated. MIME encoding intentionally differs from some AWS bugs while trying to preserve compatibility.

## Test signals
`api-headers_test.go` only checks request-id shape, so most object-header behavior relies on broader object API tests.
