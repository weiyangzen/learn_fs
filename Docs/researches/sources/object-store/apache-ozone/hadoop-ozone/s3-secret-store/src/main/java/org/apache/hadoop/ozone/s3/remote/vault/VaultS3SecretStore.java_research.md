# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/VaultS3SecretStore.java

Purpose: Implements Ozone `S3SecretStore` using HashiCorp Vault through the BetterCloud Vault Java driver.

Important APIs and control flow: Constructor builds `VaultConfig` from address, namespace, KV engine version, and SSL config; normalizes `secretPath` by trimming a trailing slash; stores `Auth`; and attempts initial authentication. `storeSecret` writes a map `{kerberosId -> awsSecret}` at `secretPath/kerberosId`. `getSecret` reads that path and returns `S3SecretValue` when the map contains the Kerberos ID. `revokeSecret` deletes the path. `callWithReAuth` executes a logical Vault call, reauthenticates once for HTTP 400/401/403, retries, and throws if auth still fails. `fromConf` builds the store from Hadoop configuration and optional TLS stores.

State and persistence behavior: Holds a mutable authenticated `Vault` client plus immutable config, auth strategy, and secret path. Secret persistence is remote Vault KV data, one path per Kerberos ID. `batcher` is unimplemented and returns null.

Dependencies and integration points: Uses `Vault`, `VaultConfig`, `LogicalResponse`, `SslConfig`, Ozone `S3SecretStore`, `S3SecretValue`, `S3Batcher`, config keys, `AuthType`, and `Auth`. It plugs into Ozone S3 secret management via `VaultS3SecretStorageProvider`.

Risks and test signals: Key risks are silent constructor auth failure after logging, null `auth` or `secretPath` producing runtime failures, treating HTTP 400 as auth failure, no batch support, and no explicit validation of Vault response structure. No tests in this subset exercise live Vault behavior.
