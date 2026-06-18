# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretFunction.java

Purpose: `S3SecretFunction` is a checked-exception-capable functional interface used to execute custom operations against an `S3SecretManager` while a caller-selected secret lock is held.

Important APIs and types: Its single method is `T accept(S3SecretManager s3SecretManager) throws IOException`. It is parameterized by return type.

Control flow: It does not implement flow directly. `S3SecretLockedManager.doUnderLock` acquires `S3_SECRET_LOCK`, invokes the function with the wrapped manager, and releases the lock in a finally block.

State and persistence behavior: The function carries no state itself, but implementations can call store, revoke, cache, or batch operations under a shared lock and thereby affect `s3SecretTable` and the secret cache.

Dependencies and integration points: This is a small adapter for Java lambdas in S3 secret and tenant workflows where multiple manager calls must be serialized.

Risks and test signals: Risks are callback misuse: long-running actions hold the write lock, and invoking a locked wrapper from inside the callback could deadlock depending on lock reentrancy. Tests should cover exception propagation and lock release on thrown `IOException`.
