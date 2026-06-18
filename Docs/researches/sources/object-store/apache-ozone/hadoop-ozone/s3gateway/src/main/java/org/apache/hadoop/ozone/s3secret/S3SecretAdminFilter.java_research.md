
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretAdminFilter.java

Purpose: JAX-RS request filter enforcing admin-only access for `@S3AdminEndpoint` resources.

Important APIs and control flow: injected `OzoneConfiguration` supplies security/admin settings. `filter` returns immediately if Ozone authorization is disabled. When authorization is enabled and a user principal exists, it creates a remote UGI from the principal name and calls `OzoneAdmins.isS3Admin`; non-admin users are aborted with HTTP 403.

State, dependencies, integration: holds injected config. Integrated by name binding and Jersey provider discovery from `Application`. Depends on `OzoneSecurityUtil`, `OzoneAdmins`, Hadoop UGI, and JAX-RS request/response APIs.

Risks and test signals: if authorization is enabled but `SecurityContext` has no principal, the current implementation does not abort, which may be intentional upstream-auth behavior but is security-sensitive. The filter trusts the container principal. No direct tests in this subset cover missing principal/admin failure for this filter.
