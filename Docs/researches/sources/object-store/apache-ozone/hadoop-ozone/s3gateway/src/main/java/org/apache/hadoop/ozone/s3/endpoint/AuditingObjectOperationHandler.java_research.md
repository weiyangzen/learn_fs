# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/AuditingObjectOperationHandler.java

Purpose: `AuditingObjectOperationHandler` wraps object-operation handlers with bucket-owner verification and audit logging.

Important APIs and flow: before each delegate call it verifies `x-amz-expected-bucket-owner` style conditions when present. It then delegates DELETE/GET/HEAD/PUT handling and logs read/write success or failure using the action stored in `ObjectRequestContext`; GET/PUT include performance data.

State, dependencies, risks, and tests: state is only the delegate reference. It integrates with `S3Owner`, object handler chains, `EndpointBase` audit helpers, and metrics/performance context. Risks include bucket-owner verification happening for subresources that may not need bucket fetch, null actions for ignored handlers, and failure logging with partially initialized context. Tests should cover expected-owner mismatch, delegated success, delegated failure, and audit action correctness.
