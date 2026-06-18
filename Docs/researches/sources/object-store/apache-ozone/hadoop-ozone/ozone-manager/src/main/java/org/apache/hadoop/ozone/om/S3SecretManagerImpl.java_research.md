# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretManagerImpl.java

Purpose: `S3SecretManagerImpl` is the store-and-cache implementation of `S3SecretManager`. It validates access IDs, reads through the cache, writes through to the configured `S3SecretStore`, and exposes the store's batcher.

Important APIs and types: Methods include `getSecret`, `getSecretString`, `storeSecret`, `revokeSecret`, `clearS3Cache`, `batcher`, `cache`, and `updateCache`. It uses `S3SecretValue`, `S3SecretStore`, `S3SecretCache`, Guava `Preconditions`, and `OzoneSecurityException` with `S3_SECRET_NOT_FOUND`.

Control flow: `getSecret` rejects blank IDs, checks cache, returns null for cached deleted markers, otherwise loads from the store and caches non-null results. `getSecretString` follows similar cache-first logic but throws `OzoneSecurityException` if the store has no entry. `storeSecret` writes to the store and then cache; `revokeSecret` deletes from the store and invalidates the cache. Direct `doUnderLock` throws because locking is provided by the wrapper.

State and persistence behavior: Persistent state lives in the store. Runtime state is the injected cache. Store writes happen before cache updates; revocation writes happen before cache invalidation.

Dependencies and integration points: It is used by OM S3 and tenant request handlers and is commonly wrapped by `S3SecretLockedManager` for concurrency control.

Risks and test signals: Cache and store can diverge if store writes succeed and cache mutation fails only partially, or if callers use the unlocked manager concurrently. `getSecretString` does not special-case deleted cached values, so deleted markers must return an appropriate secret value or be absent for this path. Tests should cover blank IDs, missing secrets, deleted cache markers, store/cache order, and unsupported direct lock callbacks.
