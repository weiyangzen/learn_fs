# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMContainerLocationFailoverProxyProvider.java

## Purpose
This class specializes generic SCM failover for `StorageContainerLocationProtocolPB` clients.

## Important APIs, Types, And Functions
The constructor passes the container PB interface, configuration, and optional `UserGroupInformation` to the base class. `getProtocolAddress(SCMNodeInfo)` selects `getScmClientAddress()`.

## Control Flow
All retry, lazy proxy construction, close, and leader failover behavior is inherited from `SCMFailoverProxyProviderBase`.

## State, Persistence, And Dependencies
No additional state is held. Dependencies include SCM node info, the storage container PB interface, and Hadoop UGI.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` uses this provider for ordinary retry-proxy calls, all-SCM admin fan-out via `getProxies()`, and targeted follower-readable calls via `getProxyForNode()`.

## Risks
Misconfigured SCM client addresses break container/admin operations. Caller-provided UGI controls RPC identity; null falls back to current user.

## Test Signals
Tests should verify address selection, UGI propagation, targeted proxy lookup, and inherited failover with container protocol calls.
