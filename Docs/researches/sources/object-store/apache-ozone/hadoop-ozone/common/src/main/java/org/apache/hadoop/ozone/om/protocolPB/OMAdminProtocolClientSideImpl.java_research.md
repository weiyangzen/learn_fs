# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/OMAdminProtocolClientSideImpl.java

Purpose: Client-side implementation of `OMAdminProtocol` for Ozone Manager administrative RPCs. It supports both targeted single-OM calls, used for node-local metadata/configuration queries, and HA failover calls, used for leader-routed operations such as OM decommissioning.

Important APIs and types: Factory methods `createProxyForSingleOM` and `createProxyForOMHA` build Hadoop protobuf RPC proxies. Public operations are `getOMConfiguration`, `decommission`, `compactOMDB`, `triggerSnapshotDefrag`, and `close`. It converts `OMNodeInfo` protos to `OMNodeDetails`, builds `OMConfiguration`, and uses admin protocol protobuf request/response types.

Control flow: Proxy creation registers `ProtobufRpcEngine`, configures retry policy from OM admin config keys, and either connects directly to one OM RPC address or wraps a `HadoopRpcOMFailoverProxyProvider` in a `RetryProxy`. Each admin method builds one protobuf request, invokes `rpcProxy`, checks success flags, and throws `IOException` with contextual OM print info on failure. Leader-related service exceptions are decoded into `OMNotLeaderException` or `OMLeaderNotReadyException` before falling back to `ProtobufHelper`.

State and persistence behavior: This class holds only an RPC proxy and printable target description. It does not persist state; persistent effects are entirely server-side: OM configuration reads, OM decommission metadata changes, RocksDB compaction, and snapshot defragmentation triggering.

Dependencies and integration points: Integrates Hadoop RPC, OM HA failover providers, `OmUtils` address resolution, OM admin protobuf service, Kerberos-authenticated PB protocol interfaces, and admin CLI flows. `close` delegates to `RPC.stopProxy`.

Risks: `getOMConfiguration` logs `ServiceException` and returns `null`, unlike most methods that throw, so callers must handle null. HA max failovers scale by OM count, so misconfigured OM addresses affect retry duration. `triggerSnapshotDefrag` treats missing `result` as a server error even when `success` is true, which is a useful protocol invariant.

Test signals: Tests should cover direct and HA proxy construction, retry policy configuration, not-leader/leader-not-ready translation, unsuccessful response error messages, null behavior on configuration query failure, and `close` stopping the proxy.
