<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java

Purpose: This is the baseline Ozone RPC client integration test class for a non-secure but ACL-enabled cluster. It inherits the shared test suite from `OzoneRpcClientTests`.

Important APIs/types/functions: The class configures `OzoneConfiguration`, enables test authorization, sets SCM pipeline owner container count to one, enables native ACLs, and calls inherited `startCluster(conf)` and `shutdownCluster()`.

Control flow: `init` builds the cluster configuration and delegates cluster startup to `OzoneRpcClientTests`. The inherited superclass supplies the actual client API tests for volumes, buckets, keys, ACLs, reads, writes, deletes, server defaults, and related RPC behavior. `shutdown` delegates cleanup.

State and persistence behavior: This file itself owns no persisted state beyond cluster lifecycle. Its effect is to run the inherited RPC client contract against a cluster with authorization and ACL behavior enabled.

Dependencies and integration points: Depends on `OzoneRpcClientTests` for behavior coverage, OM native ACL authorizer, SCM pipeline ownership settings, and MiniOzoneCluster startup.

Risks: Because this is a configuration subclass, behavioral regressions appear in inherited tests. Misconfiguring ACL or authorization flags would alter the inherited suite's expectations.

Test signals: Passing confirms the shared RPC client test suite works with native ACLs and the selected SCM pipeline/container settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java -->
