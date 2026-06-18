# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/security/TestOMDelegationTokenRequest.java

Purpose: base fixture for OM delegation-token request tests. It is not itself a test method container beyond setup/teardown, but provides common mocked OM and real metadata manager state to subclasses in the security request package.

Important APIs and types: `OzoneManager`, `OMMetadataManager`, `OmMetadataManagerImpl`, `ConfigurationSource`, `OzoneConfiguration`, `OZONE_OM_DB_DIRS`, JUnit `@TempDir`, and Mockito `framework().clearInlineMocks`.

Control flow: `setup` creates a mocked `OzoneManager`, constructs an `OzoneConfiguration` with OM DB dir pointing to a temp folder, builds `OmMetadataManagerImpl`, and stubs `ozoneManager.getMetadataManager()`. `stop` clears inline Mockito mocks.

State and persistence behavior: creates an isolated real OM metadata store rooted under the JUnit temp directory. Subclasses can use the metadata manager to validate delegation token persistence or cache behavior without sharing state across tests.

Dependencies and integration points: supports request tests for OM delegation token operations by centralizing metadata-store setup. It does not create metrics, audit logger, security managers, or token-specific state; subclasses are expected to add those as needed.

Risks covered: mostly fixture risk: wrong DB directory setup or stale mocks would make delegation-token tests flaky. There are no direct assertions in this file.

Test signals: no direct test methods; indirect signal is successful setup/teardown for subclasses that extend this fixture.
