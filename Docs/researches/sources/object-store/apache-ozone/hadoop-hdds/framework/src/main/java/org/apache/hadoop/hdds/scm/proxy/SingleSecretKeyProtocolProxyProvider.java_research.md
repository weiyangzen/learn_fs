# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SingleSecretKeyProtocolProxyProvider.java

## Purpose
`SingleSecretKeyProtocolProxyProvider` is a secret-key protocol provider pinned to one SCM node, intentionally disabling failover.

## Important APIs, Types, And Functions
The constructor records a fixed `scmNodeId` after initializing the parent provider. `getCurrentProxySCMNodeId()` always returns that id. `performFailover()` and `performFailoverToAssignedLeader()` are no-ops. `getLogger()` returns this class logger.

## Control Flow
Proxy retrieval still uses the inherited lazy creation path, but the current node id is fixed. Retry callbacks cannot move to another SCM node.

## State, Persistence, And Dependencies
The only added state is the fixed SCM node id. There is no persistence. Dependencies are the generic secret-key protocol service class, configuration, and UGI.

## Integration Points
This provider is used when secret-key access must be directed at a particular SCM rather than the HA leader/failover set.

## Risks
If the pinned node is unavailable or stale, retries cannot fail over. The constructor still loads all SCM configs through the base class, so the fixed id must exist in the loaded map.

## Test Signals
Tests should verify no failover occurs, the fixed node is used after retry callbacks, and unknown/misconfigured fixed nodes fail clearly when proxy creation is attempted.
