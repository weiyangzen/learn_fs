# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretCache.java

Purpose: `S3SecretCache` defines the cache contract for S3 secret values used by OM. It decouples `S3SecretManager` from the concrete in-memory cache and from double-buffer flush cleanup details.

Important APIs and types: The interface exposes `put`, `invalidate`, `clearCache(List<Long> transactionIds)`, and `get`. Values are `S3SecretValue` instances.

Control flow: No logic is implemented here. Implementations decide whether invalidation removes an entry or marks it deleted, and how transaction IDs are mapped to entries during clearing.

State and persistence behavior: Cache state is transient and should mirror or temporarily mask persistent `s3SecretTable` state. The transaction-ID clearing hook is designed for OM's double-buffered persistence path.

Dependencies and integration points: `S3SecretManager` default methods call this cache, `S3SecretManagerImpl` consults it before the store, and `S3SecretLockedManager` serializes cache clearing under `S3_SECRET_LOCK`.

Risks and test signals: Semantics of `invalidate` are important because the manager treats deleted cached values specially. Tests should verify each implementation's behavior for missing entries, deleted entries, flush clearing, and null cache handling through manager defaults.
