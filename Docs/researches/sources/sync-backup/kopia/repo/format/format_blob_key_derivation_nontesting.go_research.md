# sources/sync-backup/kopia/repo/format/format_blob_key_derivation_nontesting.go

## Purpose
Defines production build defaults for deriving the format encryption key from a repository password.

## Important APIs, Types, And Functions
Under `!testing`, `DefaultKeyDerivationAlgorithm` is `crypto.ScryptAlgorithm`. `SupportedFormatBlobKeyDerivationAlgorithms` returns Scrypt and PBKDF2.

## Control Flow
No dynamic control flow beyond returning a slice of supported names.

## State And Persistence
The default KDF name is persisted into new `kopia.repository` blobs when initialization does not specify one.

## Dependencies And Integration Points
Depends on `internal/crypto`. `format.Initialize` uses this default when the format blob lacks `KeyDerivationAlgorithm`.

## Risks And Edge Cases
Build tags mean tests may use a weaker default than production. Production compatibility includes both Scrypt and PBKDF2 for existing repositories or API clients.

## Test Signals
Tests under the `testing` build tag use the alternate file, so production KDF cost is not exercised by the assigned tests.
