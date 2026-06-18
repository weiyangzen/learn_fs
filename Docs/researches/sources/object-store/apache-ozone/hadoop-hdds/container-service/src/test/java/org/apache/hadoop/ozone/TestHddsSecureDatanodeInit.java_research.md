## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/TestHddsSecureDatanodeInit.java

Purpose: this test class validates secure datanode certificate-client initialization and certificate rotation behavior for `HddsDatanodeService`.

Important APIs and tests: setup enables Ozone security, configures short renewal and CA rotation intervals, uses an overridden service that mocks `createScmSecurityClient()`, captures `DNCertificateClient` logs, and prepares key/certificate storage helpers. Startup cases 0 through 7 cover combinations of missing/present private key, public key, and certificate. Rotation tests validate renewal success and recoverable failure.

Control flow and state: each test deletes key and certificate files, creates a fresh `DNCertificateClient`, then writes selected key/cert material before calling `service.initializeCertificateClient(client)`. Expected outcomes include `GETCERT`, `FAILURE`, or `SUCCESS` log signals and key/cert nullability checks. Rotation tests mock `getDataNodeCertificateChain()` and root CA lookup, start the renewer service, and wait until serial numbers change.

Persistence and integration: state is persisted in temp key and certificate directories via `KeyStorage` and `CertificateCodec`. The tests integrate SCM security protocol mocks, self-signed certificate generation, and datanode certificate-renewer scheduling.

Risks and test signals: `callQuietly()` prints and ignores setup exceptions, so failures before assertions can be noisy. The recoverable-failure test is marked flaky and uses `Thread.sleep(CERT_LIFETIME * 1000)`. These tests are high-value because they lock down secure bootstrap edge cases and renewal recovery.
