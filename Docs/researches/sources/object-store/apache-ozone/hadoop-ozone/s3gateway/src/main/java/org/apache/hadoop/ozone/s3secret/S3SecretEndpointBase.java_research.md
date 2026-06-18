
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEndpointBase.java

Purpose: base class for S3 secret REST endpoints, providing Ozone client initialization and audit-message construction.

Important APIs and control flow: constructor copies `OzoneConfiguration` and disables `S3Auth.S3_AUTH_CHECK` before client creation. `@PostConstruct initialize` creates an `OzoneClient` via `OzoneClientCache.createClient`. `userNameFromRequest` reads the security principal from the container context. Audit helpers build success/failure messages with operation, params, result, exception, and client IP when context is present. Testing setters allow injection of client and context.

State, dependencies, integration: owns an `OzoneClient`, copied config, JAX-RS `ContainerRequestContext`, and static S3G audit logger. Integrated by `S3SecretManagementEndpoint`. Depends on audit framework, `OzoneClientCache`, S3 auth constants, and `AuditUtils`.

Risks and test signals: the class disables S3 auth checks for this internal client, so HTTP/container authorization and admin filters become the critical boundary. `userNameFromRequest` assumes context, security context, and principal are non-null. There is no direct listed test for lifecycle or audit messages on secret endpoints.
