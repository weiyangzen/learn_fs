# sources/object-store/rustfs/crates/protocols/src/swift/encryption.rs

## Purpose
`encryption.rs` defines the Swift server-side encryption configuration, metadata format, and placeholder encrypt/decrypt APIs. It documents AES-256-GCM as the intended default and stores crypto metadata under `x-object-meta-crypto-*` headers.

## Important APIs, Types, And Functions
`EncryptionAlgorithm` supports `Aes256Gcm` and legacy `Aes256Cbc`, with `as_str` and a custom `from_str`. `EncryptionConfig` carries `enabled`, algorithm, key id, and a 32-byte key, with `new` and `from_env` for `SWIFT_ENCRYPTION_ENABLED`, `SWIFT_ENCRYPTION_KEY_ID`, and hex `SWIFT_ENCRYPTION_KEY`. `EncryptionMetadata` serializes/deserializes metadata headers and decodes IV/auth tags. `should_encrypt` honors global enablement and `x-object-meta-crypto-disable`. `generate_iv`, `encrypt_data`, and `decrypt_data` are public but explicitly stubbed.

## Control Flow
Callers would load config, decide whether headers require encryption, call `encrypt_data` before storing bytes, persist metadata from `EncryptionMetadata::to_headers`, then call `decrypt_data` after reading bytes and parsing metadata. The current implementation logs state transitions but returns the original input bytes unchanged.

## State, Persistence, And Dependencies
Persistent state is expected to be object metadata: algorithm, key id, IV, and optional auth tag. Configuration is process/environment state. Dependencies include base64, hex decoding, tracing, and Swift error/result types. There is no KMS integration or key registry, and only one current key id is accepted for decryption.

## Integration Points
The module is exported by `mod.rs`, but repository search in the Swift folder shows no active handler/object integration for `should_encrypt`, `encrypt_data`, or `decrypt_data`. As written, enabling the environment variable does not make `object::put_object` encrypt data.

## Risks And Test Signals
This is security-sensitive scaffolding, not functioning encryption. `generate_iv` uses timestamp-derived bytes and is not cryptographically secure; `encrypt_data`/`decrypt_data` warn that they are unimplemented and pass plaintext through; metadata may therefore misleadingly mark plaintext as encrypted if wired in prematurely. Tests validate config parsing, metadata header round trips, opt-out behavior, IV length/difference, and a passthrough round trip, but they do not assert real confidentiality or authenticated decryption failure.
