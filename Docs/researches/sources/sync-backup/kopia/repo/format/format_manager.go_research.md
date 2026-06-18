# sources/sync-backup/kopia/repo/format/format_manager.go

## Purpose
Implements the central manager for `kopia.repository` and `kopia.blobcfg`, including cached refresh, immutable crypto/hash provider exposure, mutable parameter reads, initialization, and repository config rewrites.

## Important APIs, Types, And Functions
`Manager` implements `format.Provider`. Important methods include `getOrRefreshFormat`, `maybeRefreshNotLocked`, `refresh`, `readAndCacheRepositoryBlobBytes`, provider getters, `RepositoryFormatBytes`, `GetMutableParameters`, `UpgradeLockIntent`, `RequiredFeatures`, `BlobCfgBlob`, `ObjectFormat`, `ScrubbedContentFormat`, `updateRepoConfigLocked`, `NewManager`, `NewManagerWithCache`, `Initialize`, and `randomBytes`.

## Control Flow
Reads call `maybeRefreshNotLocked`, which checks `validUntil` under a read lock and calls `refresh` when expired. Refresh reads and caches `kopia.repository`, parses JSON, wraps raw bytes with checksum for legacy embedding, derives or reuses the format key, decrypts repository config, optionally reads/decrypts blobcfg, constructs a static provider, updates current state, and initializes immutable provider on first load. Initialization verifies repository/blobcfg absence, fills default encryption/KDF/unique ID, derives the key, validates parameters and blob config, encrypts repository config, writes blobcfg, then writes repository blob.

## State And Persistence
Manager state is protected by `mu` and includes decrypted repository config, blob config, format key, current provider, cache validity, and refresh count. Persistent state is `kopia.repository` and `kopia.blobcfg`.

## Dependencies And Integration Points
Depends on `blob.Storage`, `blobCache`, encryption/hashing providers, feature flags, logging, and `gather`. It is the format source for content managers, repository initialization, password changes, retention updates, and upgrade locks.

## Risks And Edge Cases
The immutable provider is set only on first refresh, so immutable crypto/hash parameters intentionally do not change during a manager lifetime. Negative valid duration skips cache on first refresh; excessive durations are capped. `randomBytes` ignores `io.ReadFull` errors, which is low-probability but security-sensitive. Initialization writes blobcfg before repository blob, so corruption detection handles blobcfg-without-format as suspicious.

## Test Signals
`format_manager_test.go` covers cache expiry and refresh failures, retention initialization/update/validation, password changes, valid-duration capping, and accessor behavior.
