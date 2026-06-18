<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs

Purpose: core logical representation of a CryFS filesystem config.

Important APIs/types/functions: `FILESYSTEM_FORMAT_VERSION` is `0.10`. `CryConfig` stores root blob id, encryption key hex, cipher name, format/creation/last-opened versions, blocksize, filesystem id, and optional exclusive client id. Methods `serialize`, `deserialize`, and `missing_block_is_integrity_violation` delegate format handling and expose integrity mode.

Control flow: creation populates all fields; loader updates version fields and checks settings. Serialization intentionally goes through `serialization.rs`, not the derived serde impl.

State and persistence: this is the persisted config payload after encryption. Fields encode filesystem identity, block layout, crypto material, and single-client integrity mode.

Dependencies/integration: uses `byte_unit::Byte`, `FilesystemId`, and `cryfs_version::Version`.

Risks/test signals: key and cipher are strings with TODOs to use stronger types and protected memory. Format fields are strings for compatibility, which shifts validation into loader/serialization.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/cryconfig.rs -->
