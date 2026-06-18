# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientManager.java

Purpose: Caching lifecycle manager for `XceiverClientSpi` instances. It reuses connected clients per pipeline/cache-key and tracks cache metrics.

Important APIs/types/functions: Extends `XceiverClientCreator`. A Guava `Cache<String, XceiverClientSpi>` expires clients after idle threshold and caps cache size. `acquireClient` validates pipeline nodes, fetches/creates a cached client, and increments its reference count. `releaseClient` decrements references and optionally invalidates the cache entry. `getPipelineCacheKey` composes pipeline id/type, optional closest host/standalone port, and current user for security. Static `getXceiverClientMetrics` lazily creates shared client metrics. Nested `ScmClientConfig` and builder define cache sizing and stale threshold.

Control flow: Cache removal marks clients evicted. Acquire/release synchronize on the cache to coordinate reference counts and invalidation. Close invalidates all entries, unregisters cache metrics, and unregisters xceiver metrics.

State and persistence behavior: Owns client cache, cache metrics, and static process-wide xceiver metrics. Client references and eviction flags are in memory.

Dependencies and integration points: Used by Ozone client IO paths for connection pooling. Depends on Guava cache, HDDS config annotations, UGI, `CacheMetrics`, and `XceiverClientCreator`.

Risks: Removal listener only calls `setEvicted`; actual close may depend on `XceiverClientSpi` reference/eviction behavior outside this file. Cache key construction catches closest-node/current-user exceptions and continues with degraded keys, risking collisions. Static metrics lifecycle spans managers.

Test signals: Tests should cover cache reuse, invalidation, max-size eviction, idle expiration, topology-aware/EC key suffixes, security user suffix, and close unregistering metrics.
