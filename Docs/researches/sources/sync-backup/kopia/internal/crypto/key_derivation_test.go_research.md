# sources/sync-backup/kopia/internal/crypto/key_derivation_test.go

Purpose: checks HKDF master-key derivation against a fixed expected output and invalid key handling.

Important APIs/types/functions: `TestDeriveKeyFromMasterKey` with subtests `ReturnsKey`, `ErrorOnNilMasterKey`, and `ErrorOnEmptyMasterKey`.

Control flow: derives a 32-byte key from fixed master key, salt, and purpose, formats it as hex, and compares to a hard-coded expected string. Error subtests call derivation with nil and empty keys and require nil output plus an error.

State and persistence behavior: no state or persistence.

Dependencies/integration: uses `crypto.DeriveKeyFromMasterKey`, `fmt.Sprintf`, and `testify/require`.

Risks/test signals: the vector protects against accidental HKDF parameter changes. It does not test different lengths, empty salt, or AES-GCM integration.
