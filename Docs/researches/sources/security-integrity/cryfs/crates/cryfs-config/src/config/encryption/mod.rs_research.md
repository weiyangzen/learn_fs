<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs

Purpose: orchestrates two-layer config encryption/decryption and password-derived key splitting.

Important APIs/types/functions: `encrypt` builds `InnerConfig` then `OuterConfig` and serializes it. `decrypt` deserializes outer config, reads KDF parameters, derives `ConfigEncryptionKey`, decrypts outer then inner config, and returns key/params/config. `ConfigEncryptionKey` derives one combined key and exposes `outer_key` and `inner_key`.

Control flow: password KDF derives enough bytes for AES-256-GCM outer key plus maximum inner cipher key. Outer key decrypts KDF-protected wrapper; inner key closure slices bytes according to selected filesystem cipher size.

State and persistence: persists encrypted config to caller-provided writer. During load, returns KDF parameters so subsequent saves can reuse them.

Dependencies/integration: uses `PasswordBasedKDF`, `KDFParameters`, `EncryptionKey`, progress bars, `InnerConfig`, and `OuterConfig`.

Risks/test signals: TODOs mention protecting password/config key material in memory and avoiding double derivation. Tests include backward compatibility with a C++ config blob.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/mod.rs -->
