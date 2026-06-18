# sources/sync-backup/kopia/internal/repotesting/reconnectable_storage.go

Purpose: registers a blob storage wrapper used in tests to reconnect to an existing underlying storage by UUID.

Important APIs/types/functions: `reconnectableStorage`, `ReconnectableStorageType`, `ReconnectableStorageOptions`, `NewReconnectableStorage`, `ConnectionInfo`, `New`, and `init`.

Control flow: wrapping stores the underlying storage in a package `sync.Map` by UUID and returns a storage whose `ConnectionInfo` references that UUID. Reopening through registered blob provider options looks up the same backing storage.

State and persistence behavior: process-global map holds references to test storages; no external persistence.

Dependencies and integration points: used by repository tests that need close/reopen paths without real remote storage.

Risks and test signals: global map entries can leak for long test processes; UUID lookup failures should return clear errors. Tests around repository reopen exercise this indirectly.
