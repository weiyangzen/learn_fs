# sources/sync-backup/kopia/repo/format/format_set_parameters.go

## Purpose
Updates mutable repository parameters, blob storage retention configuration, and required feature flags.

## Important APIs, Types, And Functions
`Manager.SetParameters(ctx, mp, blobcfg, requiredFeatures)` is the sole function.

## Control Flow
The method locks the manager, validates mutable parameters and blob config, updates in-memory repository config fields, encrypts repository config, writes `kopia.blobcfg`, updates in-memory blob config so the following repository blob write uses new retention settings, writes `kopia.repository`, and invalidates both cache entries.

## State And Persistence
Persists encrypted repository config and encrypted blobcfg. Also updates in-memory `repoConfig` and `blobCfgBlob`.

## Dependencies And Integration Points
Depends on `internal/feature`, blob retention config, and manager encryption/write helpers. Called by repository maintenance/configuration paths that change format version, pack size, epoch parameters, or retention.

## Risks And Edge Cases
The order intentionally writes blobcfg before repository blob. If repository blob write fails after blobcfg write and in-memory blob config update, state may be partially changed. Validation happens before mutation for parameters and blob config.

## Test Signals
`format_manager_test.go` covers mutable parameter visibility through cache windows, retention update success, and invalid retention rejection.
