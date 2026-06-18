# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/auth/DirectTokenAuth.java

Purpose: `DirectTokenAuth` is the simplest Vault authentication strategy for the remote S3 secret store. It implements the `Auth` contract by taking a `Supplier<String>` token provider and applying that token directly to a BetterCloud `VaultConfig`.

Important APIs and flow: construction stores the token supplier; `auth(VaultConfig)` calls `config.token(tokenProvider.get()).build()` and returns a new `Vault`. There is no retry, caching, token renewal, or validation in this class; errors are surfaced as `VaultException` from the Vault client builder.

State, dependencies, risks, and tests: state is limited to the injected supplier, so persistence lives entirely in Vault and Ozone configuration. The class depends on `com.bettercloud.vault` and integrates with `VaultS3SecretStore` auth injection. The main risks are null/empty tokens and leaking long-lived static tokens through configuration. Test signal is indirect through Vault secret-store tests that install custom `Auth` implementations; a targeted test would assert supplier invocation and token propagation.
