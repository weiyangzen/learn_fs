# sources/sync-backup/kopia/repo/format/repository_config.go

## Purpose
Defines the encrypted repository configuration payload stored inside `kopia.repository`, including content format, object format, upgrade lock, and required feature flags.

## Important APIs, Types, And Functions
`RepositoryConfig` embeds `ContentFormat` and `ObjectFormat`, plus `UpgradeLock` and `RequiredFeatures`. `EncryptedRepositoryConfig` wraps it for JSON. Methods on `KopiaRepositoryJSON` are `decryptRepositoryConfig` and `EncryptRepositoryConfig`.

## Control Flow
Encryption JSON-marshals `EncryptedRepositoryConfig`, encrypts it with AES-GCM using the format encryption key and repository unique ID, and stores bytes in `EncryptedFormatBytes`. Decryption reverses that and returns generic errors for decrypt failure or wrapped JSON errors for invalid plaintext.

## State And Persistence
`EncryptedFormatBytes` is persisted in the public `kopia.repository` JSON. The decrypted fields include sensitive content master keys/HMAC secrets and operational fields like upgrade intent.

## Dependencies And Integration Points
Depends on `internal/feature` and format blob AES-GCM helpers. Used by `Manager.refresh`, `Initialize`, `SetParameters`, `ChangePassword`, and upgrade lock operations.

## Risks And Edge Cases
Only `AES256_GCM` is accepted here; other encryption algorithms fail. Generic decrypt errors help avoid exposing whether password/key or ciphertext was wrong. JSON schema changes must remain backward compatible with persisted configs.

## Test Signals
Format manager and password-change tests exercise successful encrypt/decrypt and invalid-password behavior through manager refresh.
