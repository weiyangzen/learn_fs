# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/proxy/SCMProxyInfo.java

## Purpose
`SCMProxyInfo` is a small value holder for one SCM RPC endpoint: service id, node id, address string, and resolved/unresolved socket address.

## Important APIs, Types, And Functions
The constructor requires a non-null `InetSocketAddress`, records string and object forms, and logs a warning when the address is unresolved. Getters expose address, service id, and node id. `toString()` returns a compact node-id/address pair.

## Control Flow
Construction performs validation and unresolved-address warning. There is no other branching.

## State, Persistence, And Dependencies
State is immutable fields. There is no persistence. Dependencies are `InetSocketAddress`, `Objects`, and SLF4J logging.

## Integration Points
`SCMFailoverProxyProviderBase` stores `SCMProxyInfo` per node id, uses it to create RPC proxies, match server-not-leader suggested leaders, and log configured endpoints.

## Risks
`rpcAddrStr` uses `InetSocketAddress.toString()`, which can include unresolved formatting. The warning is informational; unresolved addresses may still fail later at RPC connection time.

## Test Signals
Tests should verify constructor null rejection, unresolved warnings, getter values, and string formatting used in failover logs.
