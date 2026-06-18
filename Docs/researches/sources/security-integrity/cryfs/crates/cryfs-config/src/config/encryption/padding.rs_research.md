<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs

Purpose: fixed-size random padding for config encryption layers.

Important APIs/types/functions: `PADDING_OVERHEAD_PREFIX` is the binary-layout offset for the original-size field. `add_padding` prepends original size and fills remaining bytes with random data. `remove_padding` reads original size, truncates, and returns unpadded data. Errors distinguish too-small targets, missing size header, and invalid original size.

Control flow: callers allocate buffers with prefix room, serialize plaintext, then pad to a target size before encryption. On decrypt, padding is removed before parsing the inner payload.

State and persistence: padding bytes are persisted inside encrypted payloads and hide real config lengths.

Dependencies/integration: uses `binary_layout`, `rand::rng`, and `cryfs_utils::data::Data`.

Risks/test signals: padding randomness is not separately authenticated here; authentication comes from the surrounding AEAD ciphers. No local tests are present in this file, so boundary cases should be covered by encryption tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/padding.rs -->
