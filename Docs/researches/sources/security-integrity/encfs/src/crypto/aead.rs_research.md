## sources/security-integrity/encfs/src/crypto/aead.rs

Purpose: AES-256-GCM helper for wrapping and unwrapping V7 volume-key blobs using a config hash as associated authenticated data.

Important APIs and values: `GCM_NONCE_LEN`, `GCM_TAG_LEN`, `AEAD_KEY_LEN`, `encrypt`, `decrypt`. Control flow validates 32-byte key length, generates a random 96-bit nonce for encryption, encrypts in place with AAD, and returns `nonce || ciphertext || tag`; decryption splits that format and verifies the detached tag before returning plaintext.

State and persistence: Persistent output is the V7 `encrypted_key` blob in config files; nonce randomness comes from `getrandom`. Dependencies are `aes-gcm`, `anyhow`, and OS randomness. Integration is called by `EncfsConfig::set_v7_key` and `get_cipher`. Risks: key length and AAD must match exactly or configs become undecryptable; nonce uniqueness depends on OS RNG. Tests cover roundtrip, wrong key, wrong AAD, layout, and tampering of ciphertext/tag/nonce.
