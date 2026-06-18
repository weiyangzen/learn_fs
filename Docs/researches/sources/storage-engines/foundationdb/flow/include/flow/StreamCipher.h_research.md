<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/StreamCipher.h -->
# sources/storage-engines/foundationdb/flow/include/flow/StreamCipher.h

Purpose: This header wraps OpenSSL AES-GCM-style stream encryption/decryption and HMAC-SHA256 context management for Flow. It centralizes cipher key allocation, global test key handling, and arena-backed encrypted/decrypted output.

Important APIs and types: `StreamCipherKey` owns key bytes and provides `initializeKey`, `initializeRandomTestKey`, `reset`, global key allocation/cleanup, and global key accessors. `StreamCipher` owns OpenSSL `EVP_CIPHER_CTX` and `HMAC_CTX`, exposes context getters, cleanup, and a 16-byte `IV` type. `EncryptionStreamCipher`, `DecryptionStreamCipher`, and `HmacSha256StreamCipher` are reference-counted wrappers with `encrypt`/`decrypt`/`finish`.

Control flow: Keys are constructed with a size, initialized from caller bytes or deterministic random test bytes, and zeroed on reset. Encryption and decryption wrappers initialize OpenSSL contexts with a key and IV, process chunks into a provided arena, and finalize with `finish`. Static maps track context/key ids for cleanup.

State and persistence behavior: Key and context state is sensitive in-memory material. Cipher outputs are returned as arena-backed `StringRef`. Global cipher key state is process-wide and must be cleaned up. Persistent encrypted bytes are produced by callers, not by this header itself.

Dependencies and integration points: It depends on OpenSSL AES/EVP/HMAC APIs, Flow `Arena`, `FastRef`, `UID`, and deterministic random helpers. It integrates with encryption-at-rest or storage encryption paths and test-only global random key setup.

Risks: Key lifetime and cleanup are security-sensitive. `StreamCipherKey::data()` exposes mutable key bytes. Global key state can leak between tests if cleanup is missed. Arena-backed outputs require correct arena lifetime. OpenSSL context ownership must stay synchronized with static cleanup maps.

Test signals: Tests should cover encrypt/decrypt round trips, chunked processing plus `finish`, HMAC output stability, key reset zeroing, global key allocation/cleanup, invalid key/IV behavior, and deterministic test key reproducibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/StreamCipher.h -->
