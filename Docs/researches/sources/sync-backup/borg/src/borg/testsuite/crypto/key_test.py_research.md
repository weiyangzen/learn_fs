# sources/sync-backup/borg/src/borg/testsuite/crypto/key_test.py

Purpose: broad key-class contract tests covering plaintext, authenticated, legacy AES-CTR, BLAKE2/BLAKE3 authenticated variants, AEAD variants, keyfile/repokey storage, manifest/archive metadata authentication, and unsupported key-file formats.

Important APIs and control flow: `TestKey` defines mock args and a mock repository with `save_key`/`load_key`. Fixtures create keys across plaintext, authenticated, AES-CTR, BLAKE2, AES-OCB, ChaCha20-Poly1305, and BLAKE3 variants using `BORG_PASSPHRASE`. Tests validate plaintext hash/decrypt, keyfile creation and IV progression, `BORG_KEY_FILE` override, Borg 2 keyfile fixtures, BLAKE2 id hash fixture, legacy named keyfile fallback, byte-by-byte encrypted-data corruption, `identify_key`/`detect`/decrypt round trips, `assert_id`, authenticated envelope type bytes, and BLAKE2/BLAKE3 id-key sizes. `TestTAM` verifies future msgpack marker handling and legacy metadata pack/unpack without `tam`. Standalone tests cover unsupported algorithms, unsupported version 2, Argon2 key-file roundtrip through repository storage, and wrong passphrase returning `None`.

State and persistence: writes temporary key files under `BORG_KEYS_DIR` or `BORG_KEY_FILE`, stores repokey bytes in mocked repository methods, and mutates environment variables for passphrase and key location behavior.

Dependencies and integration points: depends on key classes and constants from `borg.crypto.key`, low-level `IntegrityError`, helpers `Location`, msgpack, hex/base64 conversion, and `KEY_ALGORITHMS`. It integrates with repository key storage, manifest TAM behavior, chunk id hashing, and legacy key formats.

Risks: fixture key strings and encrypted chunks are exact compatibility fixtures. Changes to key-file formatting, default storage, IV block accounting, or key type bytes must update tests deliberately. Some APIs intentionally return `None` for wrong passphrase while raising for unsupported formats, so error semantics are part of the contract.

Test signals: decryptable fixtures, expected environment-based key path behavior, corruption failures, type-byte/id-hash matches, metadata round trips, and helpful unsupported-format exceptions.
