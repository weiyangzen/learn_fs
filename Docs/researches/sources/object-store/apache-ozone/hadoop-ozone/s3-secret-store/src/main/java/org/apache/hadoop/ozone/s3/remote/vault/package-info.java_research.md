# sources/object-store/apache-ozone/hadoop-ozone/s3-secret-store/src/main/java/org/apache/hadoop/ozone/s3/remote/vault/package-info.java

Purpose: this package descriptor identifies the HashiCorp Vault-backed implementation of Ozone's remote S3 secret store. It frames the package as the Vault integration layer for storing generated S3 access secrets outside OM metadata.

Important APIs and flow: no methods are defined here. Runtime flow is through classes in the package, especially `VaultS3SecretStore`, which maps Ozone S3 secret operations to Vault logical read/write/delete calls.

State, dependencies, risks, and tests: the descriptor has no state. Package-level dependencies are BetterCloud Vault client APIs and Ozone S3 secret abstractions. The main risk is stale documentation if the implementation grows beyond Vault. Test coverage comes from `TestVaultS3SecretStore`, which exercises the package behavior against mocked Vault logical operations.
