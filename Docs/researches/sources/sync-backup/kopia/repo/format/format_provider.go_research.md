# sources/sync-backup/kopia/repo/format/format_provider.go

## Purpose
Defines repository format version constants, provider interface, and static formatting provider construction from `ContentFormat`.

## Important APIs, Types, And Functions
Constants define supported read/write versions and pack-size bounds. `Version` values are `FormatVersion1`, `FormatVersion2`, and `FormatVersion3`. `Provider` combines encryption, hashing, ECC, mutable-parameter, and repository-format-byte access. `NewFormattingOptionsProvider` validates and builds a `formattingOptionsProvider`.

## Control Flow
Provider construction clones the input content format, checks supported format and index versions, applies legacy defaults for index version and max pack size, creates hash function and encryptor, optionally wraps encryption with ECC, validates encryptor behavior by encrypting an empty payload using the empty content ID, and returns a static provider.

## State And Persistence
The provider stores cloned content format, hash function, encryptor, and original format bytes. `RepositoryFormatBytes` returns nil for password-change-capable repositories because they no longer embed format bytes in packs.

## Dependencies And Integration Points
Depends on `content/index`, `ecc`, `encryption`, `hashing`, and `gather`. `Manager.refresh` creates this provider after decrypting repository config; content managers consume it for content IDs and blob crypto.

## Risks And Edge Cases
Read and write version checks both reject unsupported versions. If ECC is enabled, the returned encryptor wrapper panics on fixed overhead. Empty-payload encryptor validation catches many misconfigurations early.

## Test Signals
Format manager tests exercise provider construction for several format versions. Encryption and ECC tests cover the lower-level algorithms used by providers.
