# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListMultipartUploadsAcls.java

Purpose: Unit tests ACL enforcement and metrics around `OzoneManager.listMultipartUploads`.

Important APIs and types: `OzoneManager`, `OmMetadataReader.checkAcls`, `KeyManager.listMultipartUploads`, `OMMetrics`, `ResolvedBucket`, S3 authentication thread-local state, `OzoneObj.ResourceType.BUCKET`, ACL types `READ` and `LIST`, and `OMException.PERMISSION_DENIED`.

Control flow: setup starts a real OM via `OmTestManagers`; each test spies it, injects mocked metadata reader/key manager/metrics through whitebox state, resolves requested bucket names to real linked bucket names, and installs audit-message mocks. Tests cover ACL-disabled bypass, ACL-enabled read-then-list ordering, READ denial, and LIST denial.

State and persistence: no key metadata is persisted for the tested call; state is the spied OM internals, S3 auth context, and metrics side effects. `AfterEach` clears S3 auth.

Dependencies and integration points: covers link-bucket resolution, S3 request context, ACL manager integration, key manager delegation, audit message construction, and operation/failure metric counters.

Risks and edge cases: ACLs must use resolved real volume/bucket names, not requested symlink names; key manager must not be called after any ACL denial; read permission must be checked before list permission; failure metrics must increment exactly on exceptions.

Test signals: Mockito verifies no ACL calls when disabled, ordered READ then LIST ACL checks when enabled, key-manager argument values with real bucket names, success/failure metric increments, and no key-manager delegation on denied access.
