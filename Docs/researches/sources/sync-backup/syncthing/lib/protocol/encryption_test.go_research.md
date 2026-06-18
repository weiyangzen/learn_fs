## sources/sync-backup/syncthing/lib/protocol/encryption_test.go

Purpose: validates deterministic encrypted names, password/file key derivation, byte encryption, encrypted file-info wrapping, and encrypted parent path detection.

Important tests/helpers: `TestEnDecryptName` checks path format, determinism, plaintext absence, and round-trip for varied name lengths. `TestKeyDerivation` verifies a known encrypted-name vector and decrypts a known byte ciphertext. `TestDecryptNameInvalid` rejects malformed encrypted paths. `TestEnDecryptBytes` checks random nonce behavior and round-trip. `encFileInfo`, `TestEnDecryptFileInfo`, `TestEncryptedFileInfoConsistency`, and `TestIsEncryptedParent` validate metadata wrapping and sentinel path recognition.

Control flow and state: tests use a package `testKeyGen`, zero keys for deterministic cases, random data for parent component lengths, and skip affected crypto tests under specific Go race-detector conditions.

Dependencies and integration points: protects protocol encryption compatibility and receive-encrypted model behavior.

Risks: known-vector tests are sensitive to crypto/library or parameter changes, which is desirable for compatibility. Race-detector skip leaves a coverage gap in affected environments.

Test signals: strong security/compatibility regression coverage for encryption helpers.
