<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go

Purpose: implements a size-bounded, TTL-based LRU cache mapping inode names to coarse metadata types for directory lookups, including regular files, symlinks, explicit directories, implicit directories, nonexistent entries, and unknown state.

Important APIs/types/functions: `Type`, constants `UnknownType`, `SymlinkType`, `RegularFileType`, `ExplicitDirType`, `ImplicitDirType`, `NonexistentType`; `TypeCache` interface; `cacheEntry`; `cacheEntry.Size`; `SizeOfTypeCacheEntry`; concrete `typeCache`; `NewTypeCache`; `Insert`; `Erase`; and `Get`.

Control flow: `NewTypeCache` disables caching when TTL is zero or max size is zero, treats `maxSizeMB == -1` as effectively unlimited, otherwise constructs an `lru.Cache` in bytes. `Insert` stores a `cacheEntry` with expiry `now + ttl`; insertion errors panic because size accounting failures indicate an internal cache invariant problem. `Get` returns `UnknownType` when disabled, missing, or expired; expired entries are erased on access. Successful lookup updates LRU recency via `lru.LookUp`.

State and persistence: state is in-memory only and guarded externally; the type states are not persisted. Cache entries include a copied key string for heap/RSS size accounting. Expiration is lazy and depends on caller-provided time, usually the filesystem cache clock.

Dependencies and integration points: depends on `internal/cache/lru` and `internal/util` for MiB conversion and unsafe size accounting. Filesystem directory inodes use this cache to avoid repeated GCS type probes and to cache nonexistent names when configured.

Risks: external synchronization is required; misuse in concurrent paths can race. Size calculation is explicitly 64-bit Linux-specific and approximates RSS as a heap conversion factor. Lazy expiration means stale entries remain until looked up or evicted. Returning `UnknownType` conflates disabled, missing, and expired states.

Test signals: `type_cache_test.go` covers constructor disabling, overwrite behavior, TTL expiration, LRU size eviction, erase/reinsert, and disabled-cache behavior for zero size or zero TTL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/type_cache.go -->
