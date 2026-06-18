<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils.go -->
# sources/object-store/minio/cmd/handler-utils.go

## Purpose
Provides shared HTTP handler utilities for region parsing, metadata extraction, event request/response element extraction, streaming content-encoding cleanup, stats collection, virtual-host resource mapping, unmatched-route errors, host naming, and proxying.

## Important APIs, types, and functions
- `parseLocationConstraint` and `isValidLocation` implement S3 bucket region validation.
- `supportedHeaders`, `validSSEReplicationHeaders`, `replicationToInternalHeaders`, and user metadata prefixes drive metadata extraction.
- Directive helpers validate COPY/REPLACE behavior.
- `extractMetadataFromReq`, `extractMetadata`, and `extractMetadataFromMime` canonicalize headers/query values into object metadata.
- `extractReqParams` and `extractRespElements` build event notification maps.
- `trimAwsChunkedContentEncoding`, `collectInternodeStats`, `collectAPIStats`, `getResource`, `extractAPIVersion`, `errorResponseHandler`, `getHostName`, and `proxyRequest` are shared handler helpers.

## Control flow
Location parsing decodes XML only when a non-empty body exists and defaults empty locations to the configured site region. Metadata extraction canonicalizes headers, copies known system headers, maps replication headers back to internal names, copies user metadata by prefix, adds a default content type, removes unencrypted length/MD5 advisory-sensitive headers, and trims `aws-chunked` from content encoding. Stats wrappers update global and per-bucket counters after handler execution. `errorResponseHandler` returns upgrade-required responses for peer/storage/admin version mismatches or generic bad-request errors for unsupported APIs.

## State and persistence behavior
No durable persistence. It mutates metadata maps, request/response stats, response headers, audit logs, and proxy request URLs. Event parameter extraction exposes principal, source IP, range, and replication-source flags.

## Dependencies and integration points
Integrates auth parsing, XML decoding, global site region, bucket metadata sys, HTTP stats, trace context, event notification, virtual-host domains, madmin admin API versioning, forwarder/proxy transport, and MinIO API error mapping.

## Risks and edge cases
Metadata canonicalization must avoid duplicate/header-case confusion and strip sensitive advisory headers. `getResource` must handle IPv6/ports and reserved minio subdomain correctly. `errorResponseHandler` is user-facing for unsupported routes and version mismatches, so message/status changes affect clients. Proxying clears local headers before forwarding.

## Test signals
`handler-utils_test.go` covers location XML parsing, metadata extraction including multiple values and nil headers, and virtual-host resource mapping for domains and IP hosts. Other behavior is integration-tested through S3/admin routing and proxy paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils.go -->
