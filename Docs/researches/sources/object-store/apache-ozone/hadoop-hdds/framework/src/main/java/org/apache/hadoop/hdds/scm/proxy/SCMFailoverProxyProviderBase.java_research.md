# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMFailoverProxyProviderBase.java

## Purpose
`SCMFailoverProxyProviderBase` implements common Hadoop `FailoverProxyProvider` behavior for SCM protobuf clients. It loads SCM HA node endpoints, lazily creates RPC proxies, tracks the current SCM node, implements round-robin and leader-hint failover, and supplies retry policy logic to Hadoop `RetryProxy`.

## Important APIs, Types, And Functions
Subclasses provide `getLogger()` and `getProtocolAddress(SCMNodeInfo)`. Public methods include `getProxy()`, `getProxies()`, `getProxyForNode()`, `performFailover()`, `performFailoverToAssignedLeader()`, `getSCMNodeIds()`, `getSCMProxyInfoList()`, `close()`, and `getRetryPolicy()`. Internal helpers load configs, create RPC proxies through `RPC.getProtocolProxy()`, and print retry messages.

## Control Flow
Construction resolves UGI, protocol version, SCM node info, endpoint maps, initial node, and retry config. `getProxy()` lazily creates the current node proxy. `performFailover()` switches to an assigned leader when known or rotates round-robin. The retry policy delegates retry/failover decisions to `SCMHAUtils`, records suggested leaders from `ServerNotLeaderException`, and emits user-facing retry messages only when another attempt will occur.

## State, Persistence, And Dependencies
State includes endpoint maps, cached `ProxyInfo` objects, node-id order, current node, retry settings, UGI, and `updatedLeaderNodeID`. There is no persistence. Dependencies include SCM HA utilities, Hadoop IPC/RPC, protobuf RPC engine, UGI, NetUtils, legacy Hadoop config conversion, and retry policy classes.

## Integration Points
All concrete SCM client providers inherit this behavior: block location, container location, SCM security, and secret-key protocols. Translators wrap these providers in Hadoop `RetryProxy`.

## Risks
Most methods are synchronized, but `updatedLeaderNodeID` is not volatile and retry callbacks can be multi-threaded. `System.err.printf` is a deliberate user-facing side effect. `getProxies()` creates every proxy and returns values from a hash map, so fan-out ordering is not deterministic. Config errors surface as runtime exceptions during proxy creation or construction.

## Test Signals
Tests should cover HA config loading, unknown node lookup, lazy creation, close stopping proxies, leader hint matching by host:port, retry action selection, no-failover retriable exceptions, round-robin behavior, and retry message content.
