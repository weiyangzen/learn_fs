# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingBucketOperationHandler.java

Purpose: `AuditingBucketOperationHandler` decorates bucket-operation handlers with consistent audit success/failure logging.

Important APIs and flow: each overridden `handleDeleteRequest`, `handleGetRequest`, and `handlePutRequest` delegates to the wrapped handler, logs write/read success with `S3RequestContext` action and performance data, and logs write/read failure when exceptions are thrown. The constructor copies dependencies between endpoint and decorator/delegate.

State, dependencies, risks, and tests: state is the delegate reference. It depends on `EndpointBase` audit helpers and action mutation by downstream handlers. Risks include logging a null or stale action if no handler claims a request, duplicate auditing for special paths like multi-delete that audit manually, and missed performance data if handlers do not populate context. Tests should verify success/failure audit calls and action selection through the bucket handler chain.
