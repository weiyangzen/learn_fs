# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/AppRoleAuth.java

Purpose: Vault authentication strategy using the AppRole auth method.

Important APIs and control flow: Constructor stores optional role auth path, role ID, and secret ID. `auth(VaultConfig config)` creates an unauthenticated `Vault`, calls `loginByAppRole(path, roleId, secretId)` when a path is configured or `loginByAppRole(roleId, secretId)` otherwise, then returns a new `Vault` built from the same config updated with the returned client token.

State and persistence behavior: Immutable auth parameters. Does not persist credentials locally; receives Vault token from remote auth response and embeds it in the returned client config.

Dependencies and integration points: Implements `Auth`, uses BetterCloud `Vault`, `VaultConfig`, `VaultException`, and `AuthResponse`. Selected by `AuthType.APP_ROLE` from Hadoop configuration.

Risks and test signals: Risks include null/invalid role ID or secret ID not being validated before the Vault call, and token renewal/lifetime being left to reauth-on-failure behavior in `VaultS3SecretStore`.
