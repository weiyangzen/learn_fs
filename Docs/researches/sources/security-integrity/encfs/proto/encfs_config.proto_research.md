## sources/security-integrity/encfs/proto/encfs_config.proto

Purpose: Protocol buffer schema for EncFS V7 configuration. It models AEAD-wrapped volume keys, Argon2 KDF parameters, block cipher mode, filename encoding, feature flags, and a config hash used as authenticated associated data.

Important APIs and types: package `encfs.v7`; messages `Config`, `Argon2Kdf`, `BasicBlockCipher`, `AesGcmSivBlockCipher`, `NameEncoding`, `FeatureFlags`; enums `BlockCipherAlgorithm` and `NameEncodingMode`; `oneof cipher` with `legacy` and `gcm_siv`. Control flow is schema-driven: `build.rs` compiles it to Rust, `config.rs` converts between generated structs and `EncfsConfig`, and V7 save/load hashes the proto with `encrypted_key` and `config_hash` cleared.

State and persistence: Defines the on-disk `.encfs7` wire contract after the `ENCFS7\0` magic. Dependencies are prost/protoc. Risks are compatibility-sensitive field numbers; changing numbers or semantics would break existing configs. The explicit `config_hash` plus AEAD AAD improves tamper detection.
