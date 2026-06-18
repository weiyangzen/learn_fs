# sources/storage-engines/rocksdb/cache/cache_key.h

## Purpose
This header defines `CacheKey`, RocksDB's fixed 16-byte cache key holder, and `OffsetableCacheKey`, a file-specific base key that efficiently derives per-offset cache keys for block and related caches.

## Important APIs, types, and functions
`CacheKey` has an empty default constructor, `IsEmpty()`, `AsSlice()` which asserts non-empty and exposes the object bytes as a 16-byte `Slice`, `CreateUniqueForCacheLifetime(Cache*)`, and `CreateUniqueForProcessLifetime()`. It stores two protected `uint64_t` words and exposes `kCacheKeySize`.

`OffsetableCacheKey` privately inherits `CacheKey` to prevent accidentally using a base key directly. It can be built from DB id/session id/file number or from a `UniqueIdPtr`, inverted with `ToInternalUniqueId()`, checked with `IsEmpty()`, converted to a concrete `CacheKey` with `WithOffset(uint64_t)` by XORing the offset into the second word, and exposed as an 8-byte common prefix with `CommonPrefixSlice()`.

## Control flow, state, and persistence
The header's inline methods are hot-path primitives with no allocation. File-derived keys are intended to be stable from table properties and suitable for persistent cache lookup; unique cache/process lifetime keys are not stable beyond their respective lifetimes.

## Dependencies and integration points
It depends on RocksDB namespace, `Slice`, `Cache`, and `UniqueId` types. Integration points include block-based table cache key setup, cache reservation manager dummy entries, cache stats collector keys, and code needing common-prefix locality for cache lookups.

## Risks and test signals
`AsSlice()` is endian-dependent and points at the object's own memory, so callers must copy if the slice outlives the object. `OffsetableCacheKey::IsEmpty()` only checks the first word and asserts consistency with the second. Misusing a base key instead of `WithOffset()` would collide all offsets, which private inheritance helps prevent. Test by comparing generated keys for uniqueness, common prefix behavior, stable table-property-derived keys, and inverse transformations.
