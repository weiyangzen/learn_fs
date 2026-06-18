# sources/storage-engines/foundationdb/fdbserver/datadistributor/ExclusionTracker.h

## Purpose
`ExclusionTracker.h` defines a small data-distributor helper that continuously tracks excluded and failed server addresses. It reads direct address exclusions and locality-based exclusions from FoundationDB system keyspace, expands locality exclusions through the storage server list, updates in-memory sets, and triggers listeners when the effective excluded/failed set changes.

The tracker is intended for Data Distributor use. Its locality expansion is based on `serverListKeys`, so the comment explicitly notes that it only sees storage processes present in the server list.

## Important APIs, Types, And Functions
`ExclusionTracker` has two public sets, `excluded` and `failed`, both `std::set<AddressExclusion>`. `changed` is an `AsyncTrigger` signaled whenever either set changes. `db` stores the database handle used for system-key reads, and `trackerFuture` owns the background actor.

The default constructor leaves the tracker inactive. The `explicit ExclusionTracker(Database db)` constructor stores the database and starts `tracker(this)`.

`isFailedOrExcluded(NetworkAddress addr)` converts the supplied address into `AddressExclusion(addr.ip, addr.port)` and checks both tracked sets.

`static Future<Void> tracker(ExclusionTracker* self)` is the long-running actor. It fetches excluded server keys, failed server keys, excluded locality keys, failed locality keys, and server list entries; decodes them; derives new excluded/failed address sets; triggers `changed` on differences; then waits on system-key watches or a polling delay.

## Control Flow
The tracker runs an infinite transaction loop. For each iteration it creates or reuses a `ReadYourWritesTransaction`, enables system key access, immediate priority, and lock awareness, then concurrently reads `excludedServersKeys`, `failedServersKeys`, `excludedLocalityKeys`, `failedLocalityKeys`, and `serverListKeys`.

Direct address exclusions are decoded with `decodeExcludedServersKey` and `decodeFailedServersKey`; invalid address exclusions are ignored. Locality exclusions are decoded into `(key,value)` pairs via `decodeLocality(decodeExcludedLocalityKey(...))` and the failed-locality equivalent.

After the server list future resolves, each `StorageServerInterface` value is decoded with `decodeServerListValue`. For every excluded locality that matches a server's locality data, the server's primary address and optional secondary address are inserted into `newExcluded`. Failed localities are expanded the same way into `newFailed`.

The actor compares `newExcluded` and `newFailed` with the current sets. Any difference replaces the stored set and triggers `changed`. It then installs watches on the four version keys (`excludedServersVersionKey`, `failedServersVersionKey`, `excludedLocalityVersionKey`, `failedLocalityVersionKey`), commits the transaction, and waits for any watch to fire. If locality exclusions exist, it also races the watches against a 10 second delay so changes in the server list can be noticed even though the server list itself is not watched.

On any error, the actor logs `ExclusionTrackerError` and calls `tr.onError(err)`, then repeats.

## State And Persistence
Persistent source of truth lives in FoundationDB system keys: direct excluded and failed server key ranges, excluded and failed locality key ranges, their version keys, and the server list. The tracker itself does not write persistent state.

In-memory state is the last effective `excluded` and `failed` set plus the `AsyncTrigger`. Locality-derived addresses are recalculated from scratch every loop. Because the actor stores only current sets, any process restart reconstructs state entirely from system keys.

The code asserts that all exclusion/locality ranges fit under `CLIENT_KNOBS->TOO_MANY` and are not returned with `more=true`.

## Dependencies And Integration Points
The header depends on Flow coroutine/actor support, `AsyncTrigger`, tracing, `Database`, `ReadYourWritesTransaction`, management API encoders/decoders, `AddressExclusion`, `NetworkAddress`, `serverListKeys`, and `StorageServerInterface` decoding.

Data Distributor and team-building code can use `isFailedOrExcluded` for address checks and wait on `changed` to react to exclusion changes. Locality exclusion integration depends on storage servers carrying locality fields in `decodeServerListValue(s.value).locality` and on the `getKeyValues` endpoint exposing primary and optional secondary addresses.

## Risks
The tracker expands locality exclusions only through the storage server list. Excluded localities for non-storage workers are intentionally outside its view. Conversely, a storage process that is down for maintenance but still in the server list can still be treated as excluded, which the code comments call out as important.

Server list changes are only polled every 10 seconds when locality exclusions are present. Direct exclusion changes are watch-driven, but locality expansion can lag behind storage recruitment/removal until the polling delay expires.

The actor takes a raw pointer to `self`; callers must keep the tracker object alive as long as `trackerFuture` can run. The sets are mutated by the actor without explicit locking, so expected use is within the Flow single-threaded actor model.

Large exclusion or server-list ranges assert under `TOO_MANY`; that is consistent with system metadata expectations but can become a hard failure if cluster metadata grows beyond the knob.

## Test Signals
Useful tests should cover direct excluded and failed addresses, invalid exclusion keys, locality exclusions matching primary and secondary storage addresses, locality changes caused by server list updates, triggering behavior when sets change versus remain equal, error retry behavior, and `isFailedOrExcluded` for both primary and secondary addresses.

Operational trace signal is `ExclusionTrackerError`; normal changes are communicated through the `changed` trigger rather than a trace event.
