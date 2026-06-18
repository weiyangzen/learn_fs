## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconDatanodeProtocolServer.java

Purpose: this class exposes Recon's DataNode-facing protocol by subclassing SCM's datanode protocol server and substituting Recon-specific binding, protocol, metrics, and authorization policy.

Important APIs and types: it implements `ReconDatanodeProtocol`, returns `ProtocolMessageMetrics` named `ReconDatanodeProtocol`, uses `OZONE_RECON_DATANODE_ADDRESS_KEY`, binds with `HddsServerUtil.getReconDataNodeBindAddress`, returns `ReconPolicyProvider`, and exposes `ReconDatanodeProtocolPB`.

Control flow: constructed by `ReconStorageContainerManagerFacade` with the facade as the SCM implementation and its `EventQueue` as the publisher. Parent server code handles RPC lifecycle; this subclass supplies the Recon-specific overrides.

State and persistence: no local persistence. Runtime RPC metrics are created for protocol message accounting.

Dependencies and integration points: feeds datanode heartbeats, reports, node reports, and pipeline reports into the event queue configured by the facade. Authorization integrates with Hadoop `PolicyProvider` through `ReconPolicyProvider`.

Risks and edge cases: incorrect address configuration can cause DataNodes to report to the wrong endpoint. The constructor passes `null` for the optional dependency accepted by the SCM parent; compatibility depends on the parent continuing to allow this mode. Policy coverage is only for the Recon datanode protocol.

Test signals: endpoint and SCM facade tests generally mock or instantiate the facade rather than this server directly. Focused tests should validate address-key selection, protocol class, and policy provider when Hadoop security is enabled.
