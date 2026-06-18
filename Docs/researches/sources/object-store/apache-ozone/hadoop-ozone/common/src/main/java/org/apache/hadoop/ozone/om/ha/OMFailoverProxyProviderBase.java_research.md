# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/OMFailoverProxyProviderBase.java

Purpose: Abstract base for OM client failover proxy providers. It owns the ordered OM proxy set, creates Hadoop RPC proxies, and supplies the retry/failover policy used when an OM is not leader, not ready, inaccessible, or returning retryable failures.

Important APIs/types/functions: Implements `FailoverProxyProvider<T>` and `Closeable`. Subclasses provide `initOmProxiesFromConfigs`. `createOMProxy` configures protobuf RPC and a network-only retry policy. `getRetryPolicy` handles `OMNotLeaderException`, `OMLeaderNotReadyException`, access-control/token failures, and Ratis read exceptions. `performFailover`, `selectNextOmProxy`, `setNextOmProxy`, `getWaitTime`, and static exception unwrappers are the main behavioral APIs.

Control flow and state: `currentProxyIndex` is the active proxy and `nextProxyIndex` is the candidate chosen by retry logic; synchronized methods protect both. Not-leader responses can jump directly to a suggested leader if the node ID/address matches known proxies. Generic retryable failures rotate round-robin. Same-OM retries use linearly increasing waits, while full rounds across all OMs trigger `waitBetweenRetries`.

State and persistence behavior: No persistent state. Runtime state includes attempted OM IDs, last attempted OM, same-OM attempt count, access-control retry tracking, and `performFailoverDone`, which prevents multiple threads from advancing the next proxy repeatedly before Hadoop's retry handler calls `performFailover`.

Dependencies and integration points: Depends on Hadoop RPC/retry APIs, Ozone configuration keys, `OMProxyInfo.OrderedMap`, Hadoop security/UGI, OM exception types, and Ratis exceptions. It is the common base for protocol-specific OM proxy providers used by Ozone clients.

Risks: Suggested leader validation requires both node ID and address, so stale or incomplete leader hints fall back to round-robin. Access-control/token errors are retried across OMs once, which avoids stale auth state but can delay failure. Any unsynchronized future changes around proxy indices would risk duplicate failovers under concurrent retries.

Test signals: Unit coverage should exercise not-leader suggested leader selection, leader-not-ready same-node backoff, round-robin retry delay after all OMs are attempted, access-control retry exhaustion, no-failover exception filtering, and concurrent `selectNextOmProxy`/`performFailover` behavior.
