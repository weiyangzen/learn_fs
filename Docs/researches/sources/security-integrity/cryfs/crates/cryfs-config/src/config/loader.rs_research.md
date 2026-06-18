<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs

Purpose: high-level config create/load/read-only workflow with version, cipher, blocksize, local-state, and single-client integrity checks.

Important APIs/types/functions: `ConfigLoadError`, `ConfigLoadResult`, `CommandLineFlags`, and public `create`, `load_or_create`, `load_readonly`. Internal `_create`, `_load`, `_check_version`, `_update_version_in_config`, `_check_cipher`, `_check_blocksize`, and `_check_missing_blocks_are_integrity_violations` implement policy.

Control flow: `load_or_create` branches on config file existence. Loading decrypts the file, clones old config, checks/migrates format version, validates expected cipher/blocksize, loads or generates filesystem metadata using the encryption key, enforces single-client mode, saves modified config if read-write, and returns client id.

State and persistence: may create encrypted config files, rewrite version/last-opened/exclusive-client fields, and update local filesystem metadata. Read-only mode suppresses config rewrites.

Dependencies/integration: integrates `CryConfigFile`, `Console`, `PasswordProvider`, `FilesystemMetadata`, `LocalStateDir`, `ClientId`, and current version constants.

Risks/test signals: many error branches are security-sensitive and currently marked TODO for tests. `filename.exists()` races with create/load. Version migration only updates version fields, not data layout beyond supported 0.10 bounds.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/loader.rs -->
