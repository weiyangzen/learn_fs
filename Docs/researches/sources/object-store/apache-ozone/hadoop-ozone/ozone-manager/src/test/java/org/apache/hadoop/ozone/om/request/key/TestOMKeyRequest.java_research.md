## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRequest.java

**Purpose:** Provides the shared fixture for OM key request tests. It creates a mocked `OzoneManager`, real/spied metadata manager, SCM block allocation mocks, metrics, key manager, snapshot manager, ACL authorizer, bucket-link resolution, and common volume/bucket/key fields.

**Important APIs/types/functions:** Uses `OzoneManager`, `OmMetadataManagerImpl`, `KeyManagerImpl`, `ScmClient`, `ScmBlockLocationProtocol`, `StorageContainerLocationProtocol`, `OMMetrics`, `OMPerformanceMetrics`, `DeletingServiceMetrics`, `OzoneManagerPrepareState`, `OzoneNativeAuthorizer`, `OMLayoutVersionManager`, `OmSnapshotManager`, and `OMRequestTestUtils`. Utility methods are `setup`, `verifyPathInOpenKeyTable`, `getBucketLayout`, `stop`, and `createSnapshot`.

**Control flow:** `@BeforeEach setup` configures temporary OM DB paths, metrics, mocked OzoneManager methods, audit logger, replication validation, SCM block allocation answers, container lookup, key manager, metadata reader, prepare state, and default random names. It also stubs bucket-link resolution for `KeyArgs` and `Pair` inputs. `createSnapshot` pre-executes and validates snapshot creation, writes response to a batch, records transaction info, commits the batch, and returns persisted `SnapshotInfo`.

**State and persistence behavior:** The fixture owns the in-test RocksDB-backed metadata manager under a temp directory. SCM allocation returns deterministic container/local IDs. Snapshot creation persists snapshot metadata and transaction info. `stop` unregisters metrics and clears Mockito inline mocks to avoid cross-test leakage.

**Dependencies and integration points:** All listed tests inherit this class directly or indirectly. It integrates request classes with real metadata table implementations while isolating external OM, SCM, security, audit, and layout dependencies behind mocks.

**Risks:** Fixture risks include mocks masking production behavior, stale inline mocks if teardown fails, deterministic block IDs causing accidental equality assumptions, and bucket-link stubs defaulting to object-store layout unless subclasses override `getBucketLayout`.

**Test signals:** Downstream tests rely on non-null metadata manager/key manager, predictable allocated block IDs, functional volume/bucket/key table helpers, successful snapshot creation, and proper cleanup after each test.
