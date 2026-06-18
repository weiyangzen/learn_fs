<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java

## Purpose
Audit action implementation for authentication and authorization events.

## Important APIs, types, and functions
- Stores request path and HTTP method.
- `fromContext` builds an action from `ContainerRequestContext`.
- `getAction` formats `AUTH(<method> <path>)`.

## Control flow
Used when auth parsing or authorization fails to build a readable audit operation name.

## State and persistence behavior
In-memory audit action only. Persistence is through audit logging infrastructure, not this class.

## Dependencies and integration points
Used by `AWSSignatureProcessor` when building auth failure messages. Implements `AuditAction`.

## Risks and edge cases
Path formatting prepends `/` to `UriInfo.getPath`; changes in JAX-RS path normalization affect audit text.

## Test signals
Auth audit tests should assert formatted action strings for root and nested object paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java -->
