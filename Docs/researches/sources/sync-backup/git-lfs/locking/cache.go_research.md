# sources/sync-backup/git-lfs/locking/cache.go

Purpose: Provides a local two-way cache of locks by path and by encoded lock ID.

Important APIs/types/functions: `LockCache`, `NewLockCache`, `Add`, `RemoveByPath`, `RemoveById`, `Locks`, `Clear`, `Save`, `encodeIdKey`, `decodeIdKey`, and `isIdKey`.

Control flow: `Add` stores the same `Lock` under path and `*id*://<id>`. Removal by either path or id looks up one side and removes both keys. `Locks` visits the KV store and returns only non-id-key entries.

State and persistence behavior: Backed by `tools/kv.Store`; mutations are in the store and `Save` persists to the configured file. `Clear` removes all entries.

Dependencies and integration points: Used by locking client code for fast local lock lookups. Depends on `kv.NewStore` and the `Lock` type.

Risks and edge cases: `Locks` type-asserts stored values to `*Lock`, so store corruption can panic. Duplicate IDs/paths overwrite prior entries. `decodeIdKey` is currently unused in this file.

Test signals: `cache_test.go` covers add, list, remove by path, and remove by id behavior.
