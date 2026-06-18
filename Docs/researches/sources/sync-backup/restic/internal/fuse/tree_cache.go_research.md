## sources/sync-backup/restic/internal/fuse/tree_cache.go

Purpose: small concurrency-safe cache that keeps FUSE child node object identity stable until FUSE forgets the node.

Important APIs/types: `treeCache` holds `map[string]fs.Node` and a mutex. `forgetFn` is a callback type. `newTreeCache` initializes the map. `lookupOrCreate` returns an existing node or calls a factory with a forget callback that deletes the name from the cache.

Control flow and state: cache entries are protected by `sync.Mutex`; the create callback is called while the mutex is held. The injected `forgetFn` deletes exactly the name being looked up.

Dependencies and integration points: used by snapshot pseudo directories and snapshot tree directories to satisfy FUSE lookup identity expectations. FUSE node implementations call `Forget` to invoke the callback.

Risks and test signals: holding the cache lock during `create` can become a deadlock risk if a constructor synchronously calls back into the same cache, though current constructors do not. `TestStableNodeObjects` validates same-object lookup and post-forget replacement.
