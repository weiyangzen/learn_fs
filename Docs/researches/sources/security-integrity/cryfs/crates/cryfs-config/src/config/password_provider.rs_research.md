<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs

Purpose: abstracts password acquisition for existing and new filesystems.

Important APIs/types/functions: `PasswordProvider` has `password_for_existing_filesystem` and `password_for_new_filesystem`. With `testutils`, `FixedPasswordProvider` returns a cloned fixed password for both paths.

Control flow: loader functions call the appropriate method before load or create, then pass the string into config encryption/decryption.

State and persistence: passwords are transient strings; TODO notes they should be protected in memory similarly to encryption keys.

Dependencies/integration: implemented by CLI-utils interactive/noninteractive password providers and used by `loader.rs`.

Risks/test signals: string-based password handling can leave sensitive material in memory. Test provider is correctly feature-gated, reducing risk of accidental production use.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/password_provider.rs -->
