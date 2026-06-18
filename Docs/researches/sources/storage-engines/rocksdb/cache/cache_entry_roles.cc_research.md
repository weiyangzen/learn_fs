# sources/storage-engines/rocksdb/cache/cache_entry_roles.cc

## Purpose
This file defines human-readable names for RocksDB cache entry roles and string keys used when reporting block cache entry statistics.

## Important APIs, types, and functions
It defines `kCacheEntryRoleToCamelString` and `kCacheEntryRoleToHyphenString`, each sized to `kNumCacheEntryRoles`, covering data blocks, filter blocks, index blocks, write buffer, compression dictionary building buffers, filter construction, table readers, file metadata, blob roles, and misc. `GetCacheEntryRoleName(CacheEntryRole)` returns the hyphenated role name. `BlockCacheEntryStatsMapKeys` returns stable map keys for cache id, capacity, last collection duration, last collection age, per-role entry counts, per-role used bytes, and per-role used percent.

## Control flow, state, and persistence
Most functions return static strings or construct prefixed strings using a local helper. There is no mutable persistent state. Returned references for fixed keys point to function-local static strings; role-derived keys are returned by value.

## Dependencies and integration points
This code integrates with `rocksdb/cache.h` role enums and block cache stats reporting. It is consumed by tools and DB properties that need stable textual keys such as `count.data-block`, `bytes.index-block`, and `percent.blob-cache`.

## Risks and test signals
The arrays must stay in enum order and size-compatible with `kNumCacheEntryRoles`; adding a role without updating both arrays would mislabel stats. String keys are external-facing and should be treated as compatibility-sensitive. Test via stats collection outputs and any tests that compare role names or map keys.
