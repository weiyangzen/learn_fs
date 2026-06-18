<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs

Purpose: fixed-size identifier for a CryFS filesystem.

Important APIs/types/functions: `FilesystemId([u8; 16])` supports `new_random`, `from_bytes`, `to_bytes`, `from_hex`, `to_hex`, serde, equality/hash, and custom `Debug` that prints hex.

Control flow: creation generates random ids; config serialization stores hex; local-state metadata uses ids as directory names and vaultdir mapping values.

State and persistence: persisted in encrypted config JSON and local-state JSON. Also used in local-state directory paths.

Dependencies/integration: uses `rand::random` for generation and `hex` for encoding/decoding.

Risks/test signals: `from_hex` rejects non-16-byte values. No local tests are present; callers rely on serde/local-state tests elsewhere. Path use of hex output is stable and filesystem-safe.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/filesystem_id.rs -->
