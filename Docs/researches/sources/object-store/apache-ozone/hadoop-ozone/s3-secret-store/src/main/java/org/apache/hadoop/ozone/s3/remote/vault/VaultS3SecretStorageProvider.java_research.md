# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStorageProvider.java

Purpose: Provider implementation that adapts the Vault-backed store to Ozone's `S3SecretStoreProvider` SPI.

Important APIs and control flow: Implements `get(Configuration conf)` and returns `VaultS3SecretStore.fromConf(conf)`. All configuration parsing and client construction is delegated.

State and persistence behavior: Stateless provider. Runtime persistence is handled by the returned Vault store against the remote Vault backend.

Dependencies and integration points: Integrates Hadoop `Configuration`, Ozone `S3SecretStore`, Ozone OM S3 provider SPI, and `VaultS3SecretStore`.

Risks and test signals: Thin wrapper with low local risk. Operational failures from missing config, auth, or Vault connectivity surface from `fromConf` as `IOException`.
