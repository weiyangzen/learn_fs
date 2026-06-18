# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/KeyLocationService.h

## Purpose
Declares an abstract key-location service for resolving keys and key ranges to storage-server location information. It is part of the client-side location cache and shard lookup boundary.

## Important APIs, Types, And Functions
`IKeyLocationService` declares `getKeyLocation()` for a single key and `getKeyRangeLocations()` for a range. Both return `Future` values containing `KeyRangeLocationInfo` data, accept tracing context and optional debug IDs, support provisional proxies, and are version-aware. `getKeyLocation()` also accepts `Reverse isBackward`, which asks for the shard containing the key before the supplied key when true.

## Control Flow
Callers pass a key or key range with the desired read version and proxy mode. Implementations consult client metadata/location caches or proxies and return location info asynchronously. Reverse single-key lookups are used for selectors that refer to the previous shard boundary.

## State And Persistence Behavior
The interface stores no local state. Implementations typically maintain in-memory location caches and read cluster metadata from system keys or proxies. Returned interfaces may be failed, as the header notes for single-key lookups.

## Dependencies And Integration Points
The header depends on `NativeAPI.actor.h` and `DatabaseContext.h` for client types, span context, provisional proxy flags, and location info. It integrates with transaction read paths, key selector resolution, shard cache refresh, and storage-server request routing.

## Risks And Test Signals
Risks include stale location information, failed interfaces in returned locations, wrong reverse-boundary handling, and version/provisional-proxy mismatches during recovery. Test signals should include shard boundary lookups, range lookup limits and reverse ordering, cache invalidation after wrong-shard errors, provisional proxy behavior, and trace/debug ID propagation.
