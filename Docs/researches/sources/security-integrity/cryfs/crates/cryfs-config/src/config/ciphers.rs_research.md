<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs

Purpose: runtime cipher-name lookup while preserving static cipher types where callers need compile-time specialization.

Important APIs/types/functions: `ALL_CIPHERS` lists `xchacha20-poly1305`, `aes-256-gcm`, and `aes-128-gcm`. `UnknownCipherError` reports unsupported names. `AsyncCipherCallback` and `SyncCipherCallback` let callers dispatch on a name. `lookup_cipher_sync`, `lookup_cipher_async`, `lookup_cipher_dyn`, and `cipher_is_supported` implement lookup variants.

Control flow: string match selects the concrete cipher type and calls the provided callback. Dynamic lookup builds a boxed `dyn Cipher` with an encryption key sized for the selected cipher.

State and persistence: no persistence; names stored in config files are validated through this module.

Dependencies/integration: uses `cryfs_crypto::symmetric` cipher definitions and encryption key handling. Used by config creation and inner config encryption/decryption.

Risks/test signals: tests verify all advertised ciphers resolve, unknown ciphers error, and selected ciphers can decrypt each other's test ciphertext only when expected type matches. TODOs note executable-size concerns and missing lookup variants.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/ciphers.rs -->
