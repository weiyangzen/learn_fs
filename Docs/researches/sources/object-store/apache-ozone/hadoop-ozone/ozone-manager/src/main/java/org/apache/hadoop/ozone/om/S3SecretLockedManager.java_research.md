# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretLockedManager.java

Purpose: `S3SecretLockedManager` decorates an `S3SecretManager` with OM lock acquisition. It centralizes lock use for S3 secret get/store/revoke/cache-clear and custom compound operations.

Important APIs and types: It implements all `S3SecretManager` methods and uses `IOzoneManagerLock` with `S3_SECRET_LOCK`. `getSecret`, `storeSecret`, `revokeSecret`, and `clearS3Cache` acquire write locks; `getSecretString` acquires a read lock; `doUnderLock` acquires a write lock and invokes `S3SecretFunction`.

Control flow: Each method acquires the relevant lock key, delegates to the wrapped manager, and releases the lock in a finally block. `clearS3Cache` uses a synthetic `"cache"` lock key. `batcher` and `cache` are simple pass-throughs.

State and persistence behavior: The wrapper has no durable state. It protects the underlying store and cache state from concurrent access within the OM process.

Dependencies and integration points: It integrates the S3 secret subsystem with `OzoneManagerLock` and request handlers that require serialized secret operations.

Risks and test signals: `getSecret` uses a write lock even though it is read-mostly, likely because cache population can mutate state. The `"cache"` lock key does not block per-secret locks, so global cache clearing relies on lock hierarchy rather than identical keys. Tests should verify lock pairing on exceptions, concurrent reads/writes, and custom callback execution under lock.
