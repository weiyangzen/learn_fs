## sources/sync-backup/kopia/internal/cache/mutex_map.go

Purpose: keyed `sync.RWMutex` registry for per-content or per-blob cache locking.

Important APIs/types/functions: `mutexMap`, `mutexMapEntry`, `exclusiveLock`, `tryExclusiveLock`, `exclusiveUnlock`, `sharedLock`, `trySharedLock`, `sharedUnlock`, `getMutexAndAddRef`, and `getMutexAndReleaseRef`.

Control flow, state, and persistence: locks create or reuse a keyed RW mutex and increment a ref count under a global mutex. Unlock paths decrement the ref count and delete the entry at zero before unlocking the keyed mutex. Try-lock failures release the reference immediately. State is in-memory only.

Dependencies and integration points: used by persistent/content cache code to coalesce same-key fetches while allowing unrelated keys to proceed.

Risks and test signals: unlock-before-keyed-unlock deletion means a new mutex for the same key can be created while the old one is still locked/unlocking, but only after ref count reaches zero. Calling unlock without a matching lock can panic or nil-deref. Tests cover exclusive/shared locking and ref cleanup.
