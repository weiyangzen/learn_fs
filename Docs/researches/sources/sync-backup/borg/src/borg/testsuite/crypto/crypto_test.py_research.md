# sources/sync-backup/borg/src/borg/testsuite/crypto/crypto_test.py

Purpose: self-test-compatible crypto test module covering low-level cipher envelopes, fixed vectors, key-file decryption, repository key detection regressions, and `KeyBase.derive_key`.

Important APIs and control flow: `CryptoTestCase` uses `BaseTestCase` without pytest imports because Borg selftest imports it directly. It tests `bytes_to_int`, `bytes_to_long`, `long_to_bytes`, `UNENCRYPTED`, `AES256_CTR_HMAC_SHA256`, `AES256_OCB`, and `CHACHA20_POLY1305`. The cipher tests build headers/AAD, encrypt fixed plaintext, slice envelope fields, compare hex MAC/IV/ciphertext vectors, validate `next_iv`, then corrupt data or AAD and require `IntegrityError`. Standalone tests construct msgpack key-file envelopes for Argon2 plus ChaCha20-Poly1305 and PBKDF2 plus AES-CTR/HMAC, then call `decrypt_key_file`. A regression test ensures `AESOCBKey.detect` treats wrong passphrase decryption as candidate failure instead of leaking low-level integrity errors. `TestDeriveKey` defines a minimal `KeyBase` subclass and verifies salt/domain/key-material separation, including `from_id_key=True`.

State and persistence: mostly in-memory. The key-detection regression uses a mocked repository with stored key bytes and environment `BORG_DISPLAY_PASSPHRASE=no`; no disk state is required.

Dependencies and integration points: depends on Cython low-level crypto classes, legacy AES/PBKDF2 code, msgpack helpers, key classes (`CHPOKey`, `AESOCBKey`, `PlaintextKey`, `KeyBase`), `getpass`, `unittest.mock`, and selftest's `BaseTestCase`. It integrates with Borg's selftest count and therefore has stricter import constraints.

Risks: fixed crypto vectors are intentionally brittle and will fail on envelope layout changes, MAC/AAD offset changes, or IV accounting changes. The selftest warning means adding/removing test methods must keep Borg's selftest metadata in sync.

Test signals: exact vector matches, corruption-triggered `IntegrityError`, successful key-file decrypt, non-raising repo-key detection, and expected derived key bytes are the primary signals.
