# sources/sync-backup/kopia/repo/format/format_manager_test.go

## Purpose
Tests format manager initialization, cache refresh semantics, mutable parameter updates, blob retention behavior, password changes, and cache duration normalization.

## Important APIs, Types, And Functions
Major tests are `TestFormatManager`, `TestInitialize`, `TestInitializeWithRetention`, `TestUpdateRetention`, `TestUpdateRetentionNegativeValue`, `TestChangePassword`, and `TestFormatManagerValidDuration`. Helpers read mutable parameters, upgrade lock intent, repository bytes, features, blob config, and raw storage bytes.

## Control Flow
`TestFormatManager` initializes storage, opens managers with shared memory cache, advances fake time around cache expiry, injects storage faults, updates parameters from another manager, and verifies visibility before/after cache expiration. Retention tests use versioned map storage to inspect retained blob settings. Password tests use two managers and cache expiry to prove old passwords fail after refresh.

## State And Persistence
Tests persist real `kopia.repository` and `kopia.blobcfg` blobs in map/versioned storage. Fake time controls cache mtimes and retention expected expiry.

## Dependencies And Integration Points
Uses `blobtesting.FaultyStorage`, `faketime`, `feature`, `gather`, default encryption/hashing, and format public APIs. It validates interactions between manager, cache, repository config encryption, and blob storage retention.

## Risks And Edge Cases
Tests cover fault injection on format/blobcfg existence checks and refresh reads. Negative retention update confirms failed validation leaves previous config in effect. Global package test variables are mutated in `TestChangePassword`, which can be order-sensitive if future tests rely on the old value without reset.

## Test Signals
Coverage is broad for manager lifecycle and state visibility. It does not cover disk cache within manager refresh; that is covered separately by cache tests.
