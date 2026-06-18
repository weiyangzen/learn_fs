# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/Auth.java

Purpose: Small strategy interface for authenticating a Vault client used by the S3 remote secret store.

Important APIs and control flow: Declares `Vault auth(VaultConfig config) throws VaultException`, returning an authenticated BetterCloud `Vault` client for a supplied base config.

State and persistence behavior: Interface has no state. Implementations may carry credentials or token suppliers.

Dependencies and integration points: Used by `VaultS3SecretStore` for initial auth and reauth, implemented by `AppRoleAuth` and token-based auth, and selected by `AuthType.fromConf`.

Risks and test signals: Minimal local risk. Implementations must be thread-safe enough for the store's use and must not leak credentials in logs.
