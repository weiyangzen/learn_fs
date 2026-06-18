# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/S3SecretStore.java

Purpose: `S3SecretStore` abstracts the durable storage backend for S3 secret values. It keeps `S3SecretManagerImpl` independent of the exact OM DB table or test store implementation.

Important APIs and types: The interface exposes `storeSecret`, `getSecret`, `revokeSecret`, and `batcher`. It stores and returns `S3SecretValue` by Kerberos/access ID string.

Control flow: Implementations perform table operations and may return null for missing secrets. `batcher` returns an `S3Batcher` when the store can participate in external batch operations, otherwise null.

State and persistence behavior: Durable state is the secret table, usually OM `s3SecretTable`. The interface itself holds no state.

Dependencies and integration points: It is injected into `S3SecretManagerImpl`, included in tenant and S3 request persistence, and represented in `OMDBDefinition`.

Risks and test signals: Store implementations must define whether `revokeSecret` is idempotent and how IO failures propagate. Tests should verify table key selection, null-on-missing behavior, batcher availability, and compatibility with cache invalidation after revocation.
