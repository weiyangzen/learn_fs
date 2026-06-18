<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs

Purpose: outer config encryption layer that stores KDF parameters and encrypts the inner config with a password-derived AES-256-GCM key.

Important APIs/types/functions: `OuterCipher` is `Aes256Gcm`. `OuterConfigLayout` stores header `cryfs.config;1;scrypt`, KDF parameters, and encrypted inner config. `OuterConfig::encrypt`, `decrypt`, `deserialize`, `serialize`, `kdf_parameters`, and helper `len` implement storage.

Control flow: inner config is serialized, padded to `CONFIG_SIZE` 1024 bytes adjusted for cipher overhead, encrypted with the outer key, and written with KDF parameters. Decryption validates header, decrypts, removes padding, and deserializes `InnerConfig`.

State and persistence: persisted bytes are the top-level `cryfs.config` file format. KDF parameters are plaintext so the password-derived key can be recomputed.

Dependencies/integration: uses `binrw`, `OuterCipher`, padding helpers, `Data`, and KDF parameter serialization.

Risks/test signals: fixed `CONFIG_SIZE` bounds must stay large enough for inner config plus overhead. Header format currently hardcodes scrypt, so adding KDFs changes compatibility surface.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/outer.rs -->
