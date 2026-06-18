# sources/sync-backup/syncthing/lib/fs/platform_common.go

## Purpose
Builds protocol platform metadata from filesystem stat ownership and extended attributes, and provides a generic expiring value cache.

## Important APIs, Types, and Functions
`unixPlatformData`, generic `valueCache[K,V]`, `cacheEntry[V]`, `newValueCache`, and `lookup`.

## Control Flow
When ownership scanning is enabled, `unixPlatformData` lstats a file, fills UID/GID, looks up owner/group names through caches, and special-cases numeric zero as `"root"` when lookup fails. When xattr scanning is enabled, it calls `fs.GetXattr` and attaches results to `protocol.PlatformData`.

## State and Persistence Behavior
Caches user/group lookups in memory for a validity duration. Does not persist metadata; returns data for protocol serialization.

## Dependencies and Integration Points
Used by Unix `BasicFilesystem.PlatformData` and `fakeFS.PlatformData`. Integrates with `protocol.PlatformData`, xattr filters, user/group caches, and filesystem stat methods.

## Risks
Lookup failures are cached as zero values, avoiding repeated lookups but potentially delaying recovery. Ownership name resolution can be stale for up to the cache validity. Xattr errors abort platform data collection.

## Test Signals
Covered indirectly by fakeFS/basicFS platform data use and xattr tests.
