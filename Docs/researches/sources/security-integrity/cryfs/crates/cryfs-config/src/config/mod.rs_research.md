<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs

Purpose: public facade for config-related modules.

Important APIs/types/functions: declares `ciphers`, `configfile`, `console`, `creator`, `cryconfig`, `encryption`, `loader`, and `password_provider`. Re-exports `ALL_CIPHERS`, config-file errors/types, `Console`, `ConfigCreateError`, `CryConfig`, `FILESYSTEM_FORMAT_VERSION`, `FilesystemId`, loader APIs, `CommandLineFlags`, `ConfigLoadResult`, and `PasswordProvider`. `FixedPasswordProvider` is re-exported behind `testutils`.

Control flow: no runtime flow; it establishes the public API used by CLI and other crates.

State and persistence: child modules own persistence.

Dependencies/integration: central import point for `cryfs-cli` and tests.

Risks/test signals: facade changes can be breaking across the workspace. Keeping test-only exports feature-gated prevents accidental production dependency on fixed passwords.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/mod.rs -->
