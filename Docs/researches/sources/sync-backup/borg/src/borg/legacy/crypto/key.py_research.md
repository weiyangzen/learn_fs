# sources/sync-backup/borg/src/borg/legacy/crypto/key.py

## Purpose
Provides Borg 1.x key compatibility classes and PBKDF2/AES-CTR key-file encryption/decryption for reading legacy repositories.

## Important APIs, Types, And Functions
`Pbkdf2FileMixin` implements `pbkdf2`, `decrypt_key_file`, `encrypt_key_file`, `decrypt_key_file_pbkdf2`, and `encrypt_key_file_pbkdf2`. `random_blake2b_256_key` creates padded BLAKE2b keys. `ID_BLAKE2b_256` supplies BLAKE2b id hashing and random initialization. Key classes are `Blake2AuthenticatedKey`, `AESCTRKey`, and `Blake2AESCTRKey`. `LEGACY_KEY_TYPES` aggregates accepted legacy key types.

## Control Flow
PBKDF2 key-file decrypt unpacks an `EncryptedKey`, checks version, stores algorithm, and for `"sha256"` derives a key, AES-decrypts data, and validates HMAC. Unsupported or non-PBKDF2 algorithms defer to superclass behavior. Encrypt mirrors this with random salt, configured iterations, HMAC, AES encryption, and msgpack packing. Key classes define accepted type bytes and cipher suites for read-only Borg 1.x compatibility.

## State And Persistence
Key instances store cryptographic key material inherited from modern key bases. PBKDF2 encryption persists encrypted key blobs. `BORG_TESTONLY_WEAKEN_KDF=1` reduces iterations for tests only.

## Dependencies And Integration Points
Depends on modern crypto key bases, low-level cipher/HMAC/BLAKE2b functions, legacy AES implementation, constants, msgpack helpers, and `EncryptedKey` items. Used by legacy repository transfer and key loading.

## Risks And Edge Cases
This is cryptography-sensitive compatibility code. Weakening KDF must remain test-only. Decrypt returns `None` on HMAC mismatch, so callers must distinguish wrong passphrase from unsupported format. Legacy key classes are read-only/not creatable despite having TYPE defaults. Random BLAKE2b keys are padded to match low-level assumptions.

## Test Signals
Legacy key tests should cover PBKDF2 encrypt/decrypt round-trip, wrong passphrase/HMAC failure, unsupported version/algorithm fallback, weak-KDF environment behavior, id hashing, random initialization lengths, and accepted type sets.
