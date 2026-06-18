<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml -->
# sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml

Purpose: manifest for `cryfs-config`, which owns encrypted config-file serialization, creation/loading policy, and local-state metadata integration.

Important APIs/types/functions: feature set has default empty and optional `testutils`. The crate exports config APIs and local-state APIs from `src/lib.rs`.

Control flow: dependencies enable binary config layouts (`binrw`, `binary-layout`), JSON/serde compatibility, scrypt KDF, symmetric crypto, hashing, byte units, and workspace versioning.

State and persistence: manifest config determines availability of filesystem config persistence, local metadata JSON, and encryption code.

Dependencies/integration: depends on `cryfs-blockstore`, `cryfs-blobstore`, `cryfs-crypto`, `cryfs-utils`, and `cryfs-version`, plus `anyhow`, `serde`, `serde_json`, `serde_with`, `rand`, `hex`, `thiserror`, and `log`.

Risks/test signals: only `tokio` dev-dependency is declared; many source files include TODOs for missing tests. Security-sensitive code relies heavily on unit tests inside ciphers/encryption and future coverage for loader/local-state errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/Cargo.toml -->
