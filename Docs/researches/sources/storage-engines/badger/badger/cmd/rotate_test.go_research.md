# sources/storage-engines/badger/badger/cmd/rotate_test.go

Purpose: validates the `rotate` command's encryption key transitions.

Important tests: `TestRotate` creates a 32-byte key, opens and closes an encrypted DB, verifies wrong old-key rotation fails with `ErrEncryptionKeyMismatch`, rotates to a second key, verifies DB opens with the new key, then rotates to plaintext and verifies an empty encryption key opens the DB. `TestRotatePlainTextToEncrypted` creates a plaintext DB with data, rotates it to an encrypted key, verifies opening without the key fails, then opens with the key and checks data is still present.

State and persistence: tests use temp DB directories and temp key files; global `oldKeyPath`, `newKeyPath`, and `sstDir` are mutated. Dependencies are Badger options, key registry behavior, random key generation, and testify. Risks: globals are not restored, so parallel tests could interfere; key files are not fsynced before use; random keys are non-deterministic. Test signals are strong for expected transition paths but do not cover malformed key lengths or missing key files.
