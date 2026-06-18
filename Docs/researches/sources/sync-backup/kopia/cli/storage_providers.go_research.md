<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_providers.go -->
# sources/sync-backup/kopia/cli/storage_providers.go

## Purpose
Defines the CLI storage provider registry, provider interfaces, common throttling flags, and app hooks for adding/listing providers.

## Important APIs, Types, And Functions
Key types are `StorageProviderServices`, `StorageFlags`, and `StorageProvider`. Key functions are `mustRegisterStorageProvider`, `registerStorageProvider`, `getRegisteredStorageProviders`, `commonThrottlingFlags`, `App.AddStorageProvider`, and `App.storageProviders`.

## Control Flow
Provider files call `mustRegisterStorageProvider` from init. The registry is guarded by a mutex, rejects duplicate names, and returns providers sorted by name. The App can also append providers at runtime for tests.

## State And Persistence Behavior
Global registry state persists for the process lifetime. App-level provider slices are mutable per app instance.

## Dependencies And Integration Points
Integrates Kingpin provider setup, blob storage interfaces, throttling limits, sync/mapping helpers, and tests that inject providers.

## Risks And Edge Cases
`AddStorageProvider` appends without duplicate checks, unlike global registration. Init-time registration order is normalized by sorting. Global state can leak across tests if tests register names directly.

## Test Signals
Tests should cover duplicate registration, sorted provider order, runtime injection, and common throttling flag binding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_providers.go -->
