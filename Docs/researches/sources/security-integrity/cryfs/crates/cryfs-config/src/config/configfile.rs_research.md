<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs

Purpose: encrypted config-file wrapper for creating, loading, mutating, and saving `CryConfig`.

Important APIs/types/functions: error enums `CreateConfigFileError`, `SaveConfigFileError`, and `LoadConfigFileError` map filesystem and serialization failures. `Access` distinguishes read-only from read-write. `CryConfigFile` stores path, config, access mode, scrypt params, `ConfigEncryptionKey`, and modified flag.

Control flow: `create_new` opens with `create_new(true)`, generates scrypt params, derives config encryption key, and writes encrypted config. `load` reads and decrypts. `config_mut` marks modified; `save_if_modified_and_has_readwrite_access` rewrites only when needed and allowed.

State and persistence: persists encrypted config files using outer/inner encryption. `save` truncates and rewrites the target path; read-only access refuses writes.

Dependencies/integration: uses `Scrypt`, `ScryptParams`, `ScryptSettings`, progress bars, and `super::encryption`. Called by loader create/load paths.

Risks/test signals: errors are structured but encryption errors collapse into serialization/deserialization wrappers. TODOs call for richer error mapping and tests, including error cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/configfile.rs -->
