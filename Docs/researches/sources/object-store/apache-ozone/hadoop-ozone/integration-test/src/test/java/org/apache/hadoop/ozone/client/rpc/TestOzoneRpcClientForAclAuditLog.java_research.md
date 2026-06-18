<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java

Purpose: This not-thread-safe integration test verifies audit log entries for Ozone client ACL APIs on volume objects, covering both successful and failed authorization paths.

Important APIs/types/functions: Setup enables audit log4j config, native ACLs, wildcard administrators, and starts a 3-datanode cluster. The test uses `OzoneAcl`, `OzoneObjInfo`, `ObjectStore.getAcl`, `addAcl`, `removeAcl`, `setAcl`, `VolumeArgs`, `OMAction`, `AuditEventStatus`, and `FileUtils` to read and clear `audit.log`.

Control flow: `testXXXAclSuccessAudits` creates a volume owned by the current user, verifies create/read audit records, constructs a volume `OzoneObj`, then performs get/add/remove/set ACL operations and verifies each audit line contains the expected action, volume, ACL identities, and `SUCCESS`. `testXXXAclFailureAudits` creates a volume owned by another user and attempts the same ACL operations; each caught exception is followed by a log assertion for `FAILURE`.

State and persistence behavior: The test mutates actual volume ACL metadata and the local `audit.log` file. `verifyLog` reads the first log line and clears the file after each assertion to isolate events.

Dependencies and integration points: Integrates ObjectStore ACL RPC APIs, native ACL authorization, OM audit logging, test log4j configuration, current `UserGroupInformation`, and filesystem log inspection.

Risks: Marked unhealthy because audit support for HA ACL code needed fixes. It is intentionally not thread-safe; any parallel audit-producing test can pollute `audit.log`. File path assumptions also depend on test working directory.

Test signals: Passing means ACL RPC success/failure paths emit audit records with expected action names, resource names, ACL identities, and statuses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java -->
