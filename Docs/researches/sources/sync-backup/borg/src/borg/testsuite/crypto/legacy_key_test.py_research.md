# sources/sync-backup/borg/src/borg/testsuite/crypto/legacy_key_test.py

Purpose: focused regression tests for Borg 1.x `Pbkdf2FileMixin` key-file encryption/decryption behavior.

Important APIs and control flow: tests instantiate legacy `AESCTRKey`, encrypt plaintext key material with passphrase and `"sha256"` algorithm, decrypt it back, confirm wrong passphrases return `None`, and pass a msgpack blob with unsupported `version=99` to require `UnsupportedKeyFormatError`.

State and persistence: all data is in-memory msgpack blobs. No key files are written.

Dependencies and integration points: depends on `borg.legacy.crypto.key.AESCTRKey`, `borg.helpers.msgpack`, and modern `UnsupportedKeyFormatError`. It supports legacy repository/key migration and compatibility handling.

Risks: wrong passphrase returning `None` is an interface contract used by key detection. Unsupported-version handling must remain an explicit error rather than silent failure.

Test signals: PBKDF2 roundtrip success, wrong-passphrase `None`, and unsupported-version exception.
