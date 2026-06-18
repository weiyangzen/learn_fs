<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs

Purpose: facade for local-state modules.

Important APIs/types/functions: declares and re-exports `LocalStateDir`, `CheckFilesystemIdError`, `VaultdirMetadata`, and `FilesystemMetadata`.

Control flow: no runtime flow.

State and persistence: child modules persist per-filesystem metadata and vaultdir mappings.

Dependencies/integration: imported by `cryfs-cli` and config loader/creator.

Risks/test signals: small compile-time facade; child modules have the substantive security and persistence risks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/mod.rs -->
