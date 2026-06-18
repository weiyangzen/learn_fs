## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconPolicyProvider.java

Purpose: `ReconPolicyProvider` supplies Hadoop service ACL metadata for Recon's datanode protocol.

Important APIs and types: extends `PolicyProvider`, exposes singleton `getInstance` through `MemoizedSupplier`, and returns one `Service` mapping `OZONE_RECON_SECURITY_CLIENT_DATANODE_CONTAINER_PROTOCOL_ACL` to `ReconDatanodeProtocol.class`.

Control flow: `ReconDatanodeProtocolServer.getPolicyProvider` returns this singleton. Hadoop RPC authorization calls `getServices` and receives a new array copy of the static service list.

State and persistence: no mutable state or persistence beyond the memoized singleton.

Dependencies and integration points: integrates with Hadoop security authorization and Recon's datanode RPC server. The ACL key comes from Recon config constants.

Risks and edge cases: only the datanode protocol is listed; additional Recon RPC protocols would need explicit service entries. Misconfigured ACLs affect DataNode communication with Recon.

Test signals: no direct test was found. A focused security test should assert that the service list contains exactly the Recon datanode protocol and expected ACL key.
