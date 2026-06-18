# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMClientConfig.java

## Purpose
`SCMClientConfig` defines typed SCM client retry and RPC timeout configuration under the `hdds.scmclient` prefix.

## Important APIs, Types, And Functions
Annotated fields include `hdds.scmclient.rpc.timeout`, `hdds.scmclient.max.retry.timeout`, `hdds.scmclient.failover.max.retry`, and `hdds.scmclient.failover.retry.interval`. Getters expose timeout, max retry timeout, retry count, and retry interval. Setters support configuration object binding.

## Control Flow
`getRetryCount()` derives an effective count from `maxRetryTimeout / retryInterval` and returns the larger of that value and configured retry count. `setRpcTimeOut()` attempts to cap overly large timeouts but checks the existing field before setting the new value.

## State, Persistence, And Dependencies
State is in-memory config object fields. Persistence is external via Ozone configuration. Dependencies are HDDS config annotations and time units.

## Integration Points
`SCMFailoverProxyProviderBase` reads this object to configure RPC timeout, retry count, and retry interval for all SCM client proxy providers.

## Risks
The `setRpcTimeOut()` cap appears ineffective for a too-large incoming `timeOut` because it tests `rpcTimeOut` rather than `timeOut`, then assigns `timeOut`. Bad retry interval values can affect retry-count math.

## Test Signals
Tests should verify config binding, effective retry count calculation, timeout capping behavior, and integration with failover retry policy delays.
