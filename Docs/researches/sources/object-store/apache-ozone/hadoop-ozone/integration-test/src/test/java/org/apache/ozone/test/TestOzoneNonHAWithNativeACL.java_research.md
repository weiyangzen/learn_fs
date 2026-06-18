# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneNonHAWithNativeACL.java

Purpose: This concrete class instantiates the `AclTests` harness as a runnable non-HA native-ACL integration suite.

Important APIs and types: It extends `AclTests`, returns `MiniOzoneCluster`, and uses JUnit `@TestInstance(PER_CLASS)`.

Control flow: `createCluster` builds the cluster from the ACL-configured builder inherited from `AclTests`, which enables native ACLs, test authorization, filesystem paths, and three datanodes.

State and persistence behavior: Persistent state comes from nested ACL tests and the ACL-enabled OM metadata they create. This class adds no state of its own.

Dependencies and integration points: It is the executable entry point for native ACL tests in a non-HA mini cluster.

Risks: It inherits global UGI mutation and shared cluster-state concerns from `AclTests`.

Test signals: Signals are inherited ACL test results for bucket ownership, volume listing, and recursive FSO ACL behavior under native ACL authorization.
