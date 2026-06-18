<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs

Purpose: crate root for CryFS config and local-state functionality.

Important APIs/types/functions: forbids unsafe code, exposes `config` and `localstate`, keeps `version` private, and re-exports `config::ALL_CIPHERS` plus `CRYFS_VERSION`.

Control flow: no runtime control flow. Public consumers enter through module APIs.

State and persistence: implemented in submodules.

Dependencies/integration: version assertion enforces Cargo/git consistency. CLI imports `CRYFS_VERSION` and config/local-state APIs from this crate.

Risks/test signals: missing-docs is a TODO. Root-level API is small; detailed risk lives in encryption, loader, and local-state modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/lib.rs -->
