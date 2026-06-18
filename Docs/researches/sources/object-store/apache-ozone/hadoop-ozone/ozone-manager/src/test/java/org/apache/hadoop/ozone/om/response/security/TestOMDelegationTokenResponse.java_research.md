# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMDelegationTokenResponse.java

Purpose: Base fixture for delegation-token response tests.

Important APIs/types/functions: Provides `ConfigurationSource conf`, `OMMetadataManager`, and `BatchOperation`. Uses `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, and `OmMetadataManagerImpl`.

Control flow: `setup` creates a temp OM metadata DB and batch. `tearDown` closes the batch.

State/persistence: Initializes the delegation token table and other OM metadata tables in a temp DB; subclasses perform actual writes.

Dependencies/integration: Shared by token response tests that need real OM metadata store persistence.

Risks/test signals: No tests directly in this class. Store itself is not explicitly closed, only batch operation.
