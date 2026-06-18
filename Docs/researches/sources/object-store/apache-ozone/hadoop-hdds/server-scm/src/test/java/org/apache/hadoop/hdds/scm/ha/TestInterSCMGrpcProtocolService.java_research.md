<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java

Purpose: This integration-style test verifies that `InterSCMGrpcProtocolService` and `InterSCMGrpcClient` use mutual TLS for SCM checkpoint download.

Important APIs and types: It uses `InterSCMGrpcProtocolService`, `InterSCMGrpcClient`, `SCMCertificateClient`, `ReloadingX509KeyManager`, `ReloadingX509TrustManager`, self-signed test certificates, mocked `StorageContainerManager`, `SCMMetadataStore`, `SCMHAManager`, `DBStore`, `DBCheckpoint`, `TypedTable`, and `TarArchiveInputStream`.

Control flow: The test allocates a free gRPC port, enables Ozone security and gRPC TLS, creates separate service and client key/certificate pairs, spies key/trust managers, starts the service, downloads a checkpoint with the client, then verifies both sides presented their certificates and validated the peer certificate. The checkpoint mock creates a directory containing `cpFile`, and the downloaded tar is opened to validate filename and content.

State and persistence behavior: Temporary certificate objects and a checkpoint directory/file are created under the test temp path. Runtime DB and HA components are mocked except the actual gRPC service/client interaction and tar stream.

Dependencies and integration points: This protects inter-SCM snapshot transfer security, certificate-client integration, DB checkpoint packaging, and transaction-info table access used during download.

Risks: The test depends on local port allocation, TLS handshake behavior, and spy call counts. Cleanup closes the client and stops the service after assertions.

Test signals: Key managers' certificate chains are requested, trust managers validate the opposite side's certificate exactly once, server does not perform server-trust validation, client does not perform client-trust validation, and the downloaded tar contains the expected checkpoint file contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestInterSCMGrpcProtocolService.java -->
