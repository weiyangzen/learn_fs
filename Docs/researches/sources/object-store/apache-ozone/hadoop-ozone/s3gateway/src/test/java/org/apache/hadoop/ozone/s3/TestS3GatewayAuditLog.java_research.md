
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestS3GatewayAuditLog.java

Purpose: tests S3 gateway audit log output for selected endpoint operations.

Important APIs and control flow: setup creates an `OzoneClientStub`, S3 bucket, shared `RequestIdentifier`, and endpoint instances via `EndpointBuilder`, overriding `getAuditParameters` for bucket/object endpoints. Tests call head bucket, root list buckets, and head object, then verify the first line in `audit.log` exactly matches expected user/ip/op/params/request-id/result formatting. `verifyLog` retries briefly for async logging and truncates the log after each assertion. `tearDown` deletes `audit.log`.

State, dependencies, integration: mutates process system property `log4j.configurationFile`, local `audit.log`, in-memory bucket content, and request identifiers. Integrates endpoint audit code and log4j config.

Risks and test signals: exact string assertions are brittle to log formatting/order changes. It checks success paths only and uses `user=null`, `ip=null` because mocked context lacks identity/IP.
