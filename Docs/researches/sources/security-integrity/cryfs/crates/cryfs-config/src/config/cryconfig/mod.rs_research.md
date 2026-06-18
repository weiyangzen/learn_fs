<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs

Purpose: module facade for core config data structures.

Important APIs/types/functions: declares `cryconfig`, `serialization`, and `filesystem_id`; re-exports `CryConfig`, `FILESYSTEM_FORMAT_VERSION`, and `FilesystemId`.

Control flow: no runtime flow. Keeps serialization internals private while exposing the stable config model.

State and persistence: persistence behavior is implemented in child modules.

Dependencies/integration: consumed by higher config modules, loader, creator, local-state, and CLI.

Risks/test signals: compile-time facade only. Any serialization API change must preserve the `CryConfig::serialize/deserialize` delegation contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/mod.rs -->
