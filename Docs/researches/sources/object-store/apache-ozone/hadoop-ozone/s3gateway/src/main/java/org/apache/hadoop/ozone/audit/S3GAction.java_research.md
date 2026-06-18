# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/S3GAction.java

Purpose: `S3GAction` enumerates audit action names for the S3 Gateway and implements the shared `AuditAction` interface.

Important APIs and flow: enum constants cover bucket APIs, root listing, object operations, multipart upload operations, secret generation/revocation, tagging, and object ACL. `getAction()` returns the enum name string used by `AuditMessage` and `AuditLogger`.

State, dependencies, risks, and tests: there is no mutable state or persistence. The enum integrates with `EndpointBase`, `S3RequestContext`, auditing handlers, and S3G audit log consumers. Risks are missing constants for newly added REST APIs or renaming values in ways that break log queries. Tests are indirect through endpoint tests and audit assertions that expect action names to be stable.
