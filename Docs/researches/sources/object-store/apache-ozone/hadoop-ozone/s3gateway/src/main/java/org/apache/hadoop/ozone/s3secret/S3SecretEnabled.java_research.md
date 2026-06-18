
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabled.java

Purpose: JAX-RS name-binding annotation for resources guarded by the S3 secret endpoint enablement flag.

Important APIs and control flow: runtime-retained, applicable to types and methods, and annotated with `@NameBinding`. It binds resources to `S3SecretEnabledEndpointRequestFilter`.

State, dependencies, integration: no state. `S3SecretManagementEndpoint` uses it at class level, so all generate/revoke operations are gated by config.

Risks and test signals: the Javadoc says "disable S3 Secure Endpoint" while the name and filter semantics mean "require endpoint enabled"; documentation wording can confuse maintainers. No direct listed test covers annotation binding.
