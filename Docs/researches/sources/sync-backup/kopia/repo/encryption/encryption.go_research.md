# sources/sync-backup/kopia/repo/encryption/encryption.go

## Purpose
Defines the content encryption interface, registry, supported algorithm listing, and HKDF-based key derivation helper.

## Important APIs, Types, And Functions
`Encryptor` requires `Encrypt`, `Decrypt`, and `Overhead`. `Parameters` supplies encryption algorithm and master key. `CreateEncryptor`, `SupportedAlgorithms`, `Register`, and `deriveKey` are the key functions. `DefaultAlgorithm` is `AES256-GCM-HMAC-SHA256`.

## Control Flow
Algorithm implementations register factories in `init`. `CreateEncryptor` looks up the selected algorithm and calls its factory. `SupportedAlgorithms` filters deprecated entries unless requested and sorts names. `deriveKey` uses HKDF-SHA256 with the repository master key, purpose bytes, empty info, and a minimum output length of 32 bytes.

## State And Persistence
The package-global `encryptors` map is in-memory registry state. No ciphertext is persisted by this file directly.

## Dependencies And Integration Points
Used by format providers, blob crypto, content managers, and ECC wrappers. It depends on `crypto/hkdf`, SHA256, `gather`, and `pkg/errors`.

## Risks And Edge Cases
Unknown algorithms fail fast. Registry mutation is not synchronized but expected during package initialization. `deriveKey` rejects too-short output lengths. Algorithm descriptions are stored but not exposed by a public API here.

## Test Signals
`encryption_test.go` exercises all registered algorithms through `SupportedAlgorithms(true)` and `CreateEncryptor`.
