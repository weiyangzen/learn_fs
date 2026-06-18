<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs

Purpose: local metadata for a known filesystem: this client's id and a salted hash of the filesystem encryption key to detect replacement.

Important APIs/types/functions: `FilesystemMetadataError::EncryptionKeyChanged`, `FilesystemMetadata { my_client_id, encryption_key }`, `load_or_generate`, `_load`, `_generate`, `_save`, `my_client_id`, `SerializedHash`, and client-id serde helpers.

Control flow: `load_or_generate` locates metadata by filesystem id. If present, it hashes the current encryption key with the stored salt and compares. On mismatch, it asks the console unless replacement is allowed; accepted replacements rewrite the stored salted hash. If absent, it generates a new random `ClientId` and salted SHA-512 hash.

State and persistence: stores JSON under `LocalStateDir::for_filesystem_id(...)/metadata`. This is local trust state, not vault data.

Dependencies/integration: uses `Sha512`, `Salt`, `EncryptionKey`, `ClientId`, `FilesystemId`, and `Console`.

Risks/test signals: no atomic write or explicit permissions are used. TODO asks for stronger error typing and tests. Hashing detects changed keys but cannot recover from local-state compromise.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/localstate/filesystem_metadata.rs -->
