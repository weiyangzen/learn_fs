# sources/storage-engines/rocksdb/cache/cache_entry_roles.h

## Purpose
This header declares the role-name arrays defined in `cache_entry_roles.cc`, making cache entry role labels available to other RocksDB components.

## Important APIs, types, and functions
It includes `<array>`, `<cstdint>`, and `rocksdb/cache.h`, then declares `extern std::array<std::string, kNumCacheEntryRoles> kCacheEntryRoleToCamelString` and `kCacheEntryRoleToHyphenString` in the RocksDB namespace.

## Control flow, state, and persistence
There is no control flow. The declarations expose global arrays whose storage is in the `.cc` file.

## Dependencies and integration points
Consumers that need direct role-name arrays include stats formatters, diagnostics, and tests. The header depends on `CacheEntryRole` and `kNumCacheEntryRoles` being visible from `rocksdb/cache.h`.

## Risks and test signals
The header uses `std::string` without including `<string>` directly, relying on transitive includes; this is usually stable through `rocksdb/cache.h` but is a include-hygiene risk. Test by compiling consumers under stricter include checks and verifying role-name arrays link exactly once.
