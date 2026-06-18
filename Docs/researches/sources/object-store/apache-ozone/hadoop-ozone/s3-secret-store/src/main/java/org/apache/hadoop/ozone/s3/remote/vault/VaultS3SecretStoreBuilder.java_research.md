# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStoreBuilder.java

Purpose: Fluent builder for `VaultS3SecretStore`, including optional Java keystore and truststore loading for Vault TLS.

Important APIs and control flow: Setter methods populate address, namespace, secret path, engine version, key/trust store settings, and `Auth`. `build` calls `loadKeyStore`, then `loadTrustStore`, and constructs `VaultS3SecretStore`. Store loaders create `SslConfig` as needed, call `loadStore`, and attach key/trust material. `loadStore` gets a `KeyStore` instance and loads from a filesystem path when provided.

State and persistence behavior: Builder holds mutable configuration until `build`. It reads keystore/truststore files from disk but writes no state. Failed store loading is logged and returns null SSL config rather than failing the build.

Dependencies and integration points: Uses BetterCloud `SslConfig`, Java `KeyStore`, `Files`, `Paths`, `InputStream`, and the Vault store/auth abstractions. It is driven by `VaultS3SecretStore.fromConf`.

Risks and test signals: Potential issue: `loadKeyStore`/`loadTrustStore` return null when corresponding type is absent, so a successfully loaded keystore can be lost if no truststore type is configured, and vice versa. `loadStore` does not call `ks.load(null, pass)` when path is null, which may leave an uninitialized keystore. Errors are logged but not surfaced.
