<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java

## Purpose
Shared helper for extracting audit parameters and client IP from JAX-RS request context.

## Important APIs, types, and functions
- `getAuditParameters` copies path and query parameters into a `Map<String, String>`.
- `getClientIpAddress` reads `ClientIpFilter.CLIENT_IP_HEADER`.

## Control flow
If context is non-null, path parameters and query parameters are iterated and their list values are stringified. Client IP lookup is a direct header read.

## State and persistence behavior
Stateless. Audit persistence happens in the audit logger, not here.

## Dependencies and integration points
Used by `AWSSignatureProcessor` for auth failure audit messages and likely by other S3 audit paths. Depends on `ContainerRequestContext` and `ClientIpFilter`.

## Risks and edge cases
Parameter values are stringified lists, not normalized scalars. Null context returns an empty parameter map but `getClientIpAddress` does not null-check context.

## Test signals
Audit tests should check path/query parameter capture, repeated query parameter formatting, and client IP header propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java -->
