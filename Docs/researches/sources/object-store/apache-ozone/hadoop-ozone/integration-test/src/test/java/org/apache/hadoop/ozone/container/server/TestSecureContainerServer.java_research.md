# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestSecureContainerServer.java

Purpose: Secure xceiver server integration tests validating block-token and container-token enforcement over gRPC and Ratis gRPC transports. It ensures unauthenticated create/read/write/block operations fail and encoded tokens allow the same requests to succeed.

Important APIs, types, and functions: The test uses `CertificateClientTestImpl`, `SecretKeyTestClient`, `OzoneBlockTokenSecretManager`, `ContainerTokenSecretManager`, `TokenVerifier`, `HddsDispatcher`, `XceiverServerGrpc`, `XceiverServerRatis`, `XceiverClientGrpc`, `XceiverClientRatis`, and container request builders for write/read/get/put block paths. Helpers include `createDispatcher`, `newXceiverServerRatis`, `runTestClientServer`, `assertRequiresToken`, `assertSucceeds`, `assertFailsTokenVerification`, and `getToken`.

Control flow: Static setup enables security and block tokens, creates certificate and secret-key clients, and initializes token managers with one-hour lifetimes. The gRPC and Ratis tests create servers for a mock pipeline, connect clients, first assert a create-container request without a container token fails, then create the container with a valid container token. They generate an all-access block token and verify write chunk, put block, read chunk, get block, and get committed block length requests fail without the encoded token and succeed with it.

State and persistence behavior: A real dispatcher and volume set are built per datanode with temp data directories. Container creation persists state before block operations. Tokens are generated from in-memory secret keys, but verification happens through production `TokenVerifier` in the dispatcher. Cleanup deletes the configured datanode data path after each test.

Dependencies and integration points: This file integrates transport security with container command authorization, Ratis datastream settings, token managers, container handlers, and low-level protobuf request builders. It also normalizes different failure surfaces: gRPC/read-only requests return response messages, while some Ratis write failures throw exceptions with token-verification text in the root cause.

Risks: Static shared configuration and mutable datanode dir cleanup require careful isolation. The test is sensitive to the definition of `isReadOnly` and to whether transport paths return failure responses or throw. Token access mode coverage uses `EnumSet.allOf`, so changes in token access semantics can alter expected success.

Test signals: Expected failures must include `BLOCK_TOKEN_VERIFICATION_FAILED`, expected successes must return `SUCCESS`, and both 1-node and 3-node Ratis pipelines must pass the same token requirements.
