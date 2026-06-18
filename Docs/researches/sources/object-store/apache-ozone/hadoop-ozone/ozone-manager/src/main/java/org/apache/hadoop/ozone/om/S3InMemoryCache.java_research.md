# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3InMemoryCache.java

Purpose: `S3InMemoryCache` is the default Guava-cache-backed implementation of `S3SecretCache`. It provides fast local lookups for S3 secrets and tombstone-like invalidation semantics for revoked secrets before double-buffer flushes make DB state authoritative.

Important APIs and types: `put`, `invalidate`, `clearCache`, and `get` implement `S3SecretCache`. It stores `S3SecretValue` by access ID or Kerberos ID in an unbounded Guava `Cache`.

Control flow: `put` directly inserts. `invalidate` uses `computeIfPresent` to replace an existing value with `secret.deleted()`, preserving a deleted marker rather than removing immediately. `clearCache` builds a transaction-log-index to cache-key map from current entries and invalidates entries whose indexes appear in the flushed transaction list. `get` returns `getIfPresent`.

State and persistence behavior: State is process-local and non-durable. Deleted entries remain visible to callers until a flush clears them, allowing `S3SecretManagerImpl.getSecret` to avoid falling back to the DB after an intentional revocation.

Dependencies and integration points: It is injected into `S3SecretManagerImpl` and controlled by double-buffer flush callbacks through `clearS3Cache`.

Risks and test signals: The cache is unbounded and `clearCache` is O(cache size + flushed IDs). Duplicate transaction log indexes would overwrite mappings. Tests should cover revoke tombstones, DB fallback suppression for deleted entries, transaction-index-based clearing, and cache consistency across store, revoke, and flush sequences.
