# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMHALeaderSpecificACLEnforcement.java

Purpose: This HA integration test proves that OM ACL and admin checks are enforced by the current leader's local configuration. It intentionally reconfigures only one OM in a three-node HA service and verifies that privileges do not implicitly follow the user after leadership transfers to a node without the same admin setting.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `OzoneClientFactory.getRpcClient`, `OzoneManager.transferLeadership`, OM reconfiguration through `getReconfigurationHandler().reconfigureProperty`, `UserGroupInformation`, `OzoneNativeAuthorizer`, `OzoneVolume`, `OzoneBucket`, `VolumeArgs`, `BucketArgs`, `OzoneOutputStream`, `OMException`, and `PERMISSION_DENIED`.

Control flow: `init` creates test and admin users, starts a three-OM HA cluster with ACLs enabled, and creates an admin-owned volume. `restoreLeadership` returns leadership to the original OM before each test. The admin-privilege test adds the test user to only the current leader's `OZONE_ADMINISTRATORS`, verifies volume and bucket creation succeeds as that user, transfers leadership to another OM, then verifies the same operations fail. The set-times test creates a key as admin, lets the test user update mtime while admin on the leader, transfers leadership, and expects `setTimes` to fail.

State and persistence behavior: Persistent OM metadata includes volumes, buckets, and keys created through the HA service. The leader-specific state is runtime OM configuration: the admin username list is reconfigured on only one process and is not treated as replicated metadata. The test also mutates the JVM login user and restores it after client operations.

Dependencies and integration points: It integrates HA leader election/transfer, client proxy routing by service ID, OM native ACL authorization, dynamic reconfiguration, admin checks for create volume/create bucket, and preExecute ACL enforcement for key `setTimes`.

Risks: Leadership transfer and user-context switching are timing-sensitive. Because the test validates intentionally node-local configuration, any future design that replicates reconfiguration would change the expected result. The static random names reduce collisions but make failures slightly harder to reproduce by name.

Test signals: Key signals are admin list membership on old and new leaders, successful object creation before transfer, `PERMISSION_DENIED` for volume/bucket creation after transfer, mtime update before transfer, unchanged privilege state on the new leader, and `PERMISSION_DENIED` from `setTimes` after leadership changes.
