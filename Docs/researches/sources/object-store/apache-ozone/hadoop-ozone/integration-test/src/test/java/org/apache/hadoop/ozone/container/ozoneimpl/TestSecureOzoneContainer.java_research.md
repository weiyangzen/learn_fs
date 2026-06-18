# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestSecureOzoneContainer.java

Purpose: Parameterized integration test for secure `OzoneContainer` command authorization. It validates how block/container token settings, token presence, and token expiry affect a create-container command sent over the gRPC xceiver client.

Important APIs, types, and functions: The class uses `OzoneContainer`, `XceiverClientGrpc`, `ContainerTokenSecretManager`, `ContainerTokenIdentifier`, `SecretKeyTestClient`, `CertificateClientTestImpl`, `MockPipeline`, `ContainerTestUtils`, and `StorageVolumeUtil`. `blockTokenOptions` enumerates combinations of `requireToken`, `hasToken`, and `tokenExpired`; `testCreateOzoneContainer` builds the container and sends the request; `testCase` provides diagnostic names.

Control flow: Static setup enables mini-cluster metrics mode. Per-test setup creates metadata paths, security cert and secret-key clients, token manager, and volume choosing policy. For each token combination, the test enables or disables `HDDS_BLOCK_TOKEN_ENABLED` and `HDDS_CONTAINER_TOKEN_ENABLED`, binds the container IPC port to the pipeline first node, creates and starts an `OzoneContainer`, and then impersonates `user1` via `UserGroupInformation.doAs`. If a token is requested, it creates a `ContainerTokenIdentifier` using the current secret key and either a future or past expiry. It sends `getCreateContainerSecureRequest` and compares response result or expected exception shape.

State and persistence behavior: Temporary metadata and data paths back real `OzoneContainer` storage. The token state is ephemeral but derived from the shared `SecretKeyTestClient`. Container lifecycle state is created only if authorization passes. Expired tokens are represented by an `Instant` in the past and may surface either as `SCMSecurityException` or a verification failure response, depending on where verification fails.

Dependencies and integration points: This is a lower-level secure container integration point between `HddsDispatcher` token verification, gRPC xceiver client, container command helpers, Hadoop UGI, certificate test client, and the local volume layout initializer.

Risks: The test depends on port binding from a mock pipeline and on different exception classes for missing versus expired tokens. Because it starts the container manually, state setup must stay aligned with real datanode layout initialization. Expiry behavior is sensitive to clock skew only at test-process scale.

Test signals: Expected outcomes are `SUCCESS` when tokens are not required or a valid token is supplied, `BLOCK_TOKEN_VERIFICATION_FAILED` when required tokens are missing or expired, `SCMSecurityException` for expired signed tokens, and `IOException` for missing-token authorization failures.
