# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestBucketRequest.java

Shared JUnit fixture for bucket request tests. It creates a mocked `OzoneManager`, temporary `OzoneConfiguration`, real `OMMetrics`, and real `OmMetadataManagerImpl`, then wires OM configuration, metrics, metadata manager, default bucket layout, replication config validation, audit logging, layout version manager, and bucket-link resolution.

The main API is `setup`, which initializes `ozoneManager`, `omMetrics`, `omMetadataManager`, and `auditLogger` for subclasses. `stop` unregisters metrics and clears Mockito inline mocks. The fixture returns `BucketLayout.fromString(OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT_DEFAULT)` as OM default bucket layout and returns a `ResolvedBucket` that maps the input pair to itself.

State is a real temporary OM metadata store, so subclasses exercise metadata tables and cache behavior instead of pure mocks. The no-op audit logger allows validateAndUpdateCache paths to log without side effects. Dependencies include `OMRequestTestUtils.setupReplicationConfigValidation`, `OMLayoutVersionManager`, `ResolvedBucket`, audit interfaces, `OmConfig`, and Mockito.

Risk is mostly fixture masking: link resolution always resolves to the same bucket and default layout is fixed unless a subclass overrides it. Tests needing link or FSO-specific semantics must seed state or override mocks explicitly. The signal is indirect: subclasses can run request preExecute and validateAndUpdateCache without missing OM plumbing.
