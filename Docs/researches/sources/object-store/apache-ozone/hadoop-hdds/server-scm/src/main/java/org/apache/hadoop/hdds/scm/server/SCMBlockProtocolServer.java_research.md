# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMBlockProtocolServer.java

Purpose: `SCMBlockProtocolServer` hosts the protobuf RPC endpoint used by OM and block clients to allocate blocks, delete key blocks, query SCM identity, add SCM peers, sort datanodes, and retrieve network topology.

Important APIs and types: It implements `ScmBlockLocationProtocol` and `Auditor`. The constructor creates an RPC server for `ScmBlockLocationProtocolPB`, registers protocol metrics, applies service ACLs, and records the resolved bind address. Main RPCs are `allocateBlock`, `deleteKeyBlocks`, `getScmInfo`, `addSCM`, `sortDatanodes`, and `getNetworkTopology`; lifecycle methods are `start`, `stop`, `join`, and `close`.

Control flow: `allocateBlock` loops `num` times through `scm.getScmBlockManager().allocateBlock`, sorts pipeline nodes by client distance when possible, audits partial allocation as failure, and records latency metrics. `deleteKeyBlocks` calls the block manager delete log and maps `SCMException` result codes to per-block delete results. `addSCM` requires admin access and delegates to the HA manager. `sortDatanodes` resolves UUIDs to datanodes and sorts by topology distance.

State and persistence behavior: The server owns RPC server state and metrics only. Block allocation/deletion persistence is delegated to `BlockManager`; HA membership persistence is delegated to `SCMHAManager`. Audit logs and metrics record outcomes.

Dependencies and integration points: It integrates Hadoop RPC, protobuf translators, SCM block manager, node manager, network topology, HA manager, security authorization, audit logging, and performance metrics.

Risks: Partial block allocation is returned but audited as failure, so clients must handle fewer blocks than requested. Client machine topology resolution may fall back to synthetic nodes or null. `stop()` also cleans up the SCM node manager, which is shared state and must align with SCM lifecycle.

Test signals: Tests should verify RPC binding, service ACL refresh, allocation success/failure metrics, client-distance pipeline ordering, delete result-code mapping, admin checks for `addSCM`, datanode sorting with unknown nodes, and audit success/failure emission.
