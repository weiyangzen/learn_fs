# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AuthType.java

Purpose: Enum and factory for selecting Vault auth strategy from Hadoop configuration.

Important APIs and control flow: Defines `APP_ROLE` and `TOKEN`. `fromConf(Configuration conf)` reads `AUTH_TYPE`, uppercases it, and switches. `TOKEN` reads `TOKEN` and returns `DirectTokenAuth` backed by a token supplier. `APP_ROLE` reads AppRole path, ID, and secret and returns `AppRoleAuth`. The default branch throws `IllegalStateException`.

State and persistence behavior: No mutable state. It maps external configuration into auth strategy objects.

Dependencies and integration points: Uses `S3SecretRemoteStoreConfigurationKeys`, Hadoop `Configuration`, `AppRoleAuth`, and token auth. Called by `VaultS3SecretStore.fromConf`.

Risks and test signals: Missing `AUTH_TYPE` causes a null dereference before a helpful error; invalid values throw `IllegalArgumentException` from `valueOf`. There is no validation for absent token, role ID, or role secret. The default switch branch is unreachable for current enum constants.
