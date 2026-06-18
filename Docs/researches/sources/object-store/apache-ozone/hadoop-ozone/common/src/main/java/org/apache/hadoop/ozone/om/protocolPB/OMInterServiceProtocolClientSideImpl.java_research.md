# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMInterServiceProtocolClientSideImpl.java

Purpose: Client-side `OMInterServiceProtocol` implementation for inter-OM bootstrap communication. It sends bootstrap metadata for a new OM node to the current OM leader through the HA RPC ring.

Important APIs and types: Constructor builds a `HadoopRpcOMFailoverProxyProvider<OMInterServiceProtocolPB>` and retry proxy. `bootstrap(OMNodeDetails)` sends `BootstrapOMRequest`; `close` closes the failover provider. It uses `BootstrapOMResponse.ErrorCode` for structured failure messages.

Control flow: Construction registers the protobuf RPC engine and uses `OZONE_CLIENT_FAILOVER_MAX_ATTEMPTS` for max failovers. `bootstrap` maps `OMNodeDetails` fields to node ID, host address, Ratis port, and listener flag, invokes `rpcProxy.bootstrap`, translates not-leader and leader-not-ready service exceptions into bootstrap-specific `IOException`s, then checks response success.

State and persistence behavior: Runtime state is the failover provider and retry proxy. The client does not persist state; successful bootstrap mutates OM cluster membership/bootstrap state on the server.

Dependencies and integration points: Integrates OM HA proxy selection, Hadoop RPC, `UserGroupInformation`, inter-service protobufs, and OM reconfiguration/bootstrap workflows.

Risks: `throwException` wraps all bootstrap failures as generic `IOException`, so callers relying on typed exceptions only get message text. Failure behavior depends on `HadoopRpcOMFailoverProxyProvider` correctly detecting leader exceptions.

Test signals: Exercise bootstrap request field mapping, failover to leader, failure response error-code propagation, leader-not-ready/not-leader handling, and provider cleanup on close.
