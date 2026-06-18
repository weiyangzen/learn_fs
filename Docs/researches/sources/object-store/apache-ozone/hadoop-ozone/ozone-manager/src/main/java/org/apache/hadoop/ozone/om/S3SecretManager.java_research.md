# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManager.java

Purpose: `S3SecretManager` is the primary OM contract for managing S3 access secrets associated with Kerberos principals or access IDs. It combines lookup, persistence, revocation, cache management, lock-scoped callbacks, and optional batch support.

Important APIs and types: Core methods are `getSecret`, `getSecretString`, `storeSecret`, `revokeSecret`, `clearS3Cache`, `doUnderLock`, `batcher`, and `cache`. Defaults include `hasS3Secret`, `isBatchSupported`, `updateCache`, `invalidateCacheEntry`, and `clearCache`.

Control flow: The interface supplies null-safe cache default methods. Concrete implementations decide store semantics, exception mapping, and whether `doUnderLock` is supported directly or only through `S3SecretLockedManager`.

State and persistence behavior: Implementations persist to `s3SecretTable` via `S3SecretStore` and maintain transient cache state through `S3SecretCache`. Batch support allows secrets to participate in atomic OM metadata writes.

Dependencies and integration points: S3 gateway authentication, tenant assignment, secret revocation requests, OM double-buffer flush handling, and audit paths all interact with this manager.

Risks and test signals: Cache defaults log access IDs and rely on implementations to avoid caching stale or deleted values. Tests should cover null cache and null batcher cases, `hasS3Secret` after revoke, secret string lookup failures, and cache clearing after transaction flushes.
