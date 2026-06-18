<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs

Purpose: creates a new in-memory `CryConfig` and local filesystem metadata before the config file is encrypted and saved.

Important APIs/types/functions: `ConfigCreateError`, `ConfigCreateResult`, and public `create`. Helpers generate an encryption key for the chosen cipher, a random root `BlobId`, and optional exclusive client id for single-client mode.

Control flow: cipher and blocksize come from command-line flags or console prompts. A random filesystem id and encryption key are generated, `FilesystemMetadata::load_or_generate` creates/checks local state, and single-client mode decides whether `exclusive_client_id` is set.

State and persistence: writes local filesystem metadata through `FilesystemMetadata`; the returned config is persisted later by `CryConfigFile::create_new`.

Dependencies/integration: uses cipher lookup callbacks, `rand::rng`, `BlobId`, `ClientId`, `EncryptionKey`, `LocalStateDir`, and current CryFS/filesystem versions.

Risks/test signals: key generation uses `rand::rng()` with a TODO about RNG choice. Blocksize validity is not checked here. Tests are TODO.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/creator.rs -->
