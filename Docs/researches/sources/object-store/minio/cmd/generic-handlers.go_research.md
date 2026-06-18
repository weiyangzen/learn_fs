<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers.go -->
# sources/object-store/minio/cmd/generic-handlers.go

## Purpose
Defines generic HTTP middleware and request classifiers used before S3/admin/KMS handlers. It enforces request/header limits, rejects malicious or reserved requests, redirects browser users, forwards federated buckets and site-replication multipart requests, adds response headers, and catches panics.

## Important APIs, types, and functions
- Limit constants define max body, header, user metadata, and bucket counts.
- `containsReservedMetadata` and `isHTTPHeaderSizeTooLarge` validate request metadata.
- `setRequestLimitMiddleware`, `setBrowserRedirectMiddleware`, `setRequestValidityMiddleware`, `setBucketForwardingMiddleware`, `addCustomHeadersMiddleware`, `setCriticalErrorHandler`, and `setUploadForwardingMiddleware` are middleware layers.
- Request classifiers include `guessIsBrowserReq`, `guessIsHealthCheckReq`, `guessIsMetricsReq`, `guessIsRPCReq`, `isAdminReq`, and `isKMSReq`.
- Helpers include `getRedirectLocation`, `parseAmzDateHeader`, `hasBadHost`, `hasBadPathComponent`, and `hasMultipleAuth`.

## Control flow
The limit middleware rejects reserved internal metadata and over-large headers before wrapping the body with `MaxBytesReader`. Validity middleware rejects bad hosts, dot/dot-dot path components, bad query values, multiple auth mechanisms, unauthorized access to reserved buckets, invalid bucket names, and SSE-C over plaintext. Browser middleware redirects anonymous browser GET/HEAD requests to the console for selected resources. Federation middleware looks up bucket DNS in etcd-backed config and proxies to a remote host if the bucket belongs elsewhere. Upload forwarding decodes the deployment ID from multipart upload IDs and proxies to the initiating site-replication peer.

## State and persistence behavior
The middleware mutates HTTP responses, request URLs for proxying, and global rejected-request counters. It reads global browser, DNS/federation, domain, TLS, site-replication, and forwarder state. It does not persist durable data.

## Dependencies and integration points
Integrates S3 auth detection, crypto SSE-C detection, MinIO grid routes, metrics routes, DNS store, forwarding transport, audit logging, trace context, global HTTP stats, bucket helpers, and admin/KMS route prefixes.

## Risks and edge cases
This is security-sensitive. Operator precedence in `guessIsMetricsReq` means later metric paths are accepted regardless of auth type unless intentionally relying on route protection elsewhere. Path validation trims Unicode whitespace and limits 32 KiB paths. Reserved metadata allows only mapped replication headers. Proxy branches must clear response headers before forwarding to avoid leaking local headers.

## Test signals
`generic-handlers_test.go` covers RPC route detection, header/user-metadata size limits, reserved metadata detection, SSE-C-over-HTTP rejection, and `hasBadPathComponent` benchmark cases. Federation and upload forwarding need integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/generic-handlers.go -->
