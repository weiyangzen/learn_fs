# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/volume/TestOMVolumeResponse.java

Purpose: Shared fixture for OM volume response tests. It provides a temporary on-disk OM metadata store and a reusable DB batch for subclasses.

Important APIs and types: `@TempDir`, `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, `OmMetadataManagerImpl`, `OMMetadataManager`, and `BatchOperation`.

Control flow: `setup` creates an `OzoneConfiguration`, points OM DB directories at the JUnit temp path, constructs `OmMetadataManagerImpl`, and initializes a batch operation from the store. `tearDown` closes the batch when present. Protected getters expose the metadata manager and batch to tests.

State and persistence behavior: The fixture creates a real local RocksDB-backed metadata manager, not just mocks, so subclasses verify actual table and batch semantics. The only persistent state is temporary test DB data scoped to each test.

Risks: The batch is shared per test method and must be manually committed by subclasses that expect durable results. Test signal is indirect: subclasses rely on this setup to produce isolated metadata state and avoid leaking open batch resources.
