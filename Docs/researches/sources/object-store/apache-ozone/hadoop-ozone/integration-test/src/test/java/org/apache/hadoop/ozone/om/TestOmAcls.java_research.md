# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmAcls.java

Purpose: This integration test verifies OM ACL enforcement and audit/log signals for denied volume, bucket, key, file-status, and key ACL operations. It uses a custom authorizer whose per-resource booleans can be flipped to force negative authorization outcomes.

Important APIs and types: The suite uses `MiniOzoneCluster`, `OzoneConfiguration`, `OZONE_TEST_AUTHORIZATION_ENABLED`, `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS`, wildcard administrators, `IAccessAuthorizer`, `OzoneObjInfo`, `RequestContext`, `OzoneAcl`, `ObjectStore`, `OzoneBucket`, `TestDataUtil`, `OMException`, `ResultCodes.PERMISSION_DENIED`, `AuditLogTestUtils`, `OMAction`, and `LogCapturer`.

Control flow: Cluster setup enables ACLs and installs `OzoneAccessAuthorizerTest`, then stores the actual authorizer from the OM. Before each test it clears captured logs/audit logs and resets all resource booleans to allow. Individual tests turn off one resource class, perform an operation that needs create/read/write/read-ACL/write-ACL permission, assert `OMException`, inspect the error log text, and verify relevant audit failure records where present. The nested authorizer returns allow/deny based solely on resource type: volume, bucket, key, or prefix.

State and persistence behavior: Successful setup creates volumes, buckets, and keys needed before flipping denial flags. The important mutable state is the in-memory authorizer booleans and audit log file content. The test does not inspect metadata tables; it validates that operations are blocked before or during OM request processing with the expected result code.

Dependencies and integration points: It integrates OM native ACL call sites, object-store client APIs, file-status lookup, key ACL management operations (`getAcl`, `setAcl`, `addAcl`, `removeAcl`), audit logging, and OM log messages.

Risks: The custom authorizer ignores ACL type and identity, so the tests validate OM call-site routing and denial handling rather than real ACL policy semantics. Assertions on log substrings can break when diagnostic text changes even if authorization remains correct.

Test signals: Signals include `PERMISSION_DENIED`, log messages naming the missing permission and resource type, audit failures for create/read/set/get/add/remove ACL operations, and correct use of volume, bucket, or key resource type in the test authorizer.
