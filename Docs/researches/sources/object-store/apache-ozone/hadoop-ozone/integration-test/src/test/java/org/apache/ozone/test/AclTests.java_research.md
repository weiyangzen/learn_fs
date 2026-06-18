# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/AclTests.java

Purpose: This abstract integration harness runs selected OM ACL tests with native Ozone ACL authorization enabled on a shared non-HA mini cluster.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>`, uses `OzoneConfiguration`, `UserGroupInformation`, `OZONE_TEST_AUTHORIZATION_ENABLED`, `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS_NATIVE`, and `OMConfigKeys.OZONE_OM_ENABLE_FILESYSTEM_PATHS`. Nested classes extend `TestBucketOwner`, `TestOzoneManagerListVolumes`, and `TestRecursiveAclWithFSO`.

Control flow: `newClusterBuilder` sets three datanodes. `createOzoneConfig` logs in the admin user, enables test authorization, native ACLs, and filesystem paths, then returns the configuration. `loginAdmin` resets the login user before each test. Nested test classes override `cluster()` to return the shared cluster from the harness.

State and persistence behavior: The harness persists cluster state created by nested ACL tests and globally changes the Hadoop login user to `om` in group `ozone` before config creation and before each test. ACL metadata and filesystem-path behavior are exercised by nested test suites.

Dependencies and integration points: It integrates Ozone native ACL authorizer configuration with existing OM ACL test classes while sharing one mini cluster. It depends on test security mode to avoid Kerberos while still enforcing ACL checks.

Risks: Global `UserGroupInformation.setLoginUser` can affect tests if not reset by the harness. The nested tests share a cluster, so cleanup and unique names are important. The harness only covers the selected nested ACL suites.

Test signals: Signals are inherited from the nested ACL suites: bucket owner behavior, list-volume authorization, and recursive ACL behavior in FSO mode under native ACL enforcement.
