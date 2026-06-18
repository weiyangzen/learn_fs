# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/S3SecretRemoteStoreConfigurationKeys.java

Purpose: Defines string constants for configuring the remote Vault-backed S3 secret store.

Important APIs and control flow: Final utility class with private constructor. Constants use prefix `ozone.secret.s3.store.remote.vault.` and cover Vault address, namespace, secret path, auth type, token, AppRole ID/secret/path, KV engine version, truststore type/path/password, and keystore type/path/password.

State and persistence behavior: No mutable state. These keys are read from Hadoop `Configuration` by `VaultS3SecretStore.fromConf` and `AuthType.fromConf`.

Dependencies and integration points: Shared by Vault store, builder, and auth selection code. It forms the external configuration contract for operators.

Risks and test signals: No tests in this subset directly validate spelling or required-key behavior. Missing or null configuration values flow into auth parsing and Vault client construction, so validation is deferred to consumers.
