# sources/user-network-fs/blobfuse2/component/attr_cache/cacheMap.go

Purpose: defines the per-path cache entry used by `AttrCache`. It stores the cached object attributes, the cache timestamp, and bitmap flags indicating whether the entry is valid and whether the path exists.

Important APIs/types/functions: constants `AttrFlagUnknown`, `AttrFlagExists`, and `AttrFlagValid` define bitmap positions. `attrCacheItem` contains `attr *internal.ObjAttr`, `cachedAt time.Time`, and `attrFlag common.BitMap64`. `newAttrCacheItem` initializes a valid positive or negative entry. Methods include `valid`, `exists`, `markDeleted`, `invalidate`, `getAttr`, `isDeleted`, `setSize`, and `setMode`.

Control flow: positive entries are created with both valid and exists bits set. Negative entries are valid but not exists. `markDeleted` converts any item into a valid negative entry with empty attributes and a supplied deletion timestamp. `invalidate` clears validity and resets attributes to an empty object. `setSize` and `setMode` update selected attributes and refresh `cachedAt`.

State and persistence behavior: entries are pure in-memory state and are stored in `AttrCache.cacheMap`. The timestamp drives both `GetAttr` staleness checks and background cleanup. There is no per-entry mutex, deep-copying, or persistence.

Dependencies/integration: depends on `common.BitMap64`, `internal.ObjAttr`, `os.FileMode`, and `time`. It is tightly coupled to `attr_cache.go`, which decides when to call the mutating methods.

Risks: methods mutate `attr`, `attrFlag`, and timestamps without their own locking; callers must provide synchronization. `getAttr` returns the stored pointer directly, so external callers can observe shared state. `setSize` and `setMode` assume `attr` is non-nil and suitable for mutation; callers check `valid` and `exists` before these calls in current code.

Test signals: `attr_cache_test.go` asserts deleted, invalid, untouched, chmod, truncate, and rename behaviors by directly inspecting this structure. Race and pointer-aliasing behavior is not tested.
