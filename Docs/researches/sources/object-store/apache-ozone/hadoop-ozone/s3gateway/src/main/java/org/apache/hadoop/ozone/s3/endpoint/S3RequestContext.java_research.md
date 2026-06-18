<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java

## Purpose
Per-request context object shared by object operation handlers for timing, action selection, lazy volume lookup, and performance logging.

## Important APIs, types, and functions
- Captures `startNanos` at construction.
- Holds `PerformanceStringBuilder`, `EndpointBase`, mutable `S3GAction`, and cached `OzoneVolume`.
- `getVolume` lazily calls `endpoint.getVolume`.
- `ignore(@Nullable S3GAction)` stores non-null handler actions and tells handlers whether to skip a request.

## Control flow
Endpoint entry points create a context with a best-guess action. Subresource handlers call `ignore` with their detected action; if non-null, the action is updated for audit logging and the handler processes the request.

## State and persistence behavior
Only in-memory per-request state is stored. It does not modify Ozone state directly.

## Dependencies and integration points
Used by `ObjectEndpoint`, `ObjectOperationHandlerChain`, tagging, ACL, multipart, and auditing handlers. Depends on `EndpointBase`, `S3GAction`, and Ozone client volume objects.

## Risks and edge cases
The mutable action is central to audit correctness. If a handler forgets to call `ignore` or sets the wrong action, the operation may be logged and metered incorrectly.

## Test signals
Audit tests should verify operation names for normal objects and subresources. Handler dispatch tests should ensure lazy volume/bucket lookups do not happen for ignored handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java -->
