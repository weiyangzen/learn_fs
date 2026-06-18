# sources/storage-engines/foundationdb/fdbclient/DatabaseContext.cpp

## Purpose

`DatabaseContext.cpp` implements a large part of the native FoundationDB client database context. It owns client-side state shared by transactions, watches, GRV caching, special key-space registration, client status reporting, TSS request duplication/mismatch handling, storage-server interface caching, health metric caching, and periodic trace counters. It is the concrete runtime backing for `Database` references created from client cluster metadata or from an internal server-side `ClientDBInfo`.

The file is actor-heavy. Long-lived actors run beside the context to log metrics, monitor proxy set changes, publish sampled client transaction status, and react to TSS mismatches. The destructor cancels those actors and breaks reference cycles explicitly, so lifetime and cancellation semantics are part of the implementation contract.

## Important APIs, types, and functions

- Watch metadata API:
  - `DatabaseContext::getWatchMetadata()`, `setWatchMetadata()`, `deleteWatchMetadata()` maintain `watchMap`.
  - `increaseWatchRefCount()` and `decreaseWatchRefCount()` maintain `watchCounterMap` by `WatchMapKey` and `Version`. When the last version reference goes away, `decreaseWatchRefCount()` cancels `WatchMetadata::watchFutureSS` and removes metadata to avoid a future waiting on state that keeps itself alive.
- TSS state:
  - `addTssMapping()` maps a storage server UID to a TSS interface, creates `TSSMetrics`, and updates `queueModel` endpoint duplication for data and non-data storage RPC endpoints.
  - `removeTssMapping()` removes the mapping and removes all duplicated queue-model endpoints.
  - `tssLogger()` periodically traces per-pair metrics, latency sketches, and error histograms, then clears the sample window.
  - `handleTssMismatches()` consumes `tssMismatchStream`, writes mismatch evidence to system key-backed maps, and either quarantines or kills the TSS by setting `tssQuarantineKeyFor()` or clearing `serverTagKeyFor()`.
- Version-vector and read-version cache:
  - `addSSIdTagMapping()`, `getLatestCommitVersionForSSID()`, `getLatestCommitVersion()`, and `getLatestCommitVersions()` expose storage-server commit-version information from `ssVersionVectorCache`.
  - `updateCachedReadVersion()`, `getCachedReadVersion()`, and `getLastGrvTime()` update/read the GRV cache either from context fields or from `DatabaseSharedState` under a mutex.
  - `validateVersion()` rejects version `0`, old versions after a switchable cluster changed, and invalid versions except `latestVersion`.
- Storage server interface cache:
  - `StorageServerInfo::getInterface()` interns `StorageServerInterface` objects by server UID in `DatabaseContext::server_interf`, updating an interface in place when only the endpoint token changes and replacing it when locality changes.
  - `StorageServerInfo::~StorageServerInfo()` unregisters itself from the context unless the context already called `notifyContextDestroyed()`.
- Health and special keys:
  - `getHealthMetricsActor()`, `DatabaseContext::getHealthMetrics()`, and `getStorageStats()` cache aggregate and detailed health metrics from GRV proxies.
  - `SingleSpecialKeyImpl` adapts a single-key async getter into a `SpecialKeyRangeReadImpl`.
  - `HealthMetricsRangeImpl` exposes aggregate, tlog, and storage health JSON under `\xff\xff/metrics/health/`.
  - `registerSpecialKeysImpl()` registers module implementations conditionally on API version and deprecation version.
- Client status persistence:
  - `TrInfoChunk` stores chunk key/value pairs for persisted client latency/status payloads.
  - `transactionInfoCommitActor()` writes chunks with `SetVersionstampedKey` and updates `client_latency_counter/`.
  - `delExcessClntTxnEntriesActor()` trims old `client_latency/` entries based on a byte counter and configured limit.
  - `clientStatusUpdateActor()` drains `clientStatusUpdater.inStatusQ`, chunks large values under `VALUE_SIZE_LIMIT`, commits bounded transaction batches, samples cleanup through global config, and explicitly resets `Transaction` objects to release context references.
- Proxy-change validation:
  - `assertFailure()` and `attemptGRVFromOldProxies()` send causal-read-risky GRV requests to old GRV proxies and assert if an old proxy still returns a read version after a recovery that has completed.
  - `monitorClientDBInfoChange()` watches `ClientDBInfo`, triggers proxy-change notifications, clears `ssVersionVectorCache`, and probabilistically runs the old-proxy GRV check.
- Lifecycle:
  - The primary `DatabaseContext` constructor initializes counters, caches, actors, `GlobalConfig`, `SpecialKeySpace`, special-key implementations gated by API version, and periodic throttle expiry.
  - The error constructor builds a context that carries `deferredError`.
  - `DatabaseContext::create()` is the server/internal factory.
  - The destructor cancels background actors, releases shared state, notifies cached `StorageServerInfo` objects, clears location cache, and traces destruction.

## Control flow

Initialization starts in the main constructor. It records connection/client metadata, initializes counters and latency sketches, sets the initial `connected` future based on proxy availability, sizes metadata and location caches from knobs, starts `databaseLogger() && tssLogger()`, starts `monitorClientDBInfoChange()`, `handleTssMismatches()`, and `clientStatusUpdateActor()`, constructs `GlobalConfig`, and registers special key-space implementations according to API version gates (`>= 740`, `>= 700`, `>= 630`) and deprecation gates.

Read-version cache updates are monotonic. Both shared and local cache paths only accept a version greater than or equal to the cached version. Time is updated only if the request start time is newer than the last GRV time. Consumers use `getCachedReadVersion()` and `getLastGrvTime()` with shared-state locking when applicable.

Latest commit-version calculation starts from `LocationInfo` storage-server IDs. `getLatestCommitVersions()` only returns data if the read version came from a GRV proxy and the version-vector cache has data. It validates that the read version is not newer than the cache maximum unless GRV cache use makes that expected. It groups tags by commit version and writes an ordered `VersionVector`.

Client status reporting loops forever. Each cycle waits for a connected database, refreshes a transaction, swaps the input status queue into an output queue, splits serialized status payloads into versionstamped chunks, commits chunks in bounded batches, handles `transaction_too_large` by halving the batch byte limit, samples cleanup according to global config, resets the transaction, and sleeps. Errors are traced; cancellation is rethrown, and non-cancellation failures delay before retry.

TSS mismatch handling is event driven. The actor reads detailed mismatch batches from `tssMismatchStream`, finds the paired source storage server in `tssMapping`, builds a `ReadYourWritesTransaction` with system-key access, updates quarantine/kill state and mismatch maps, retries through `onError()`, and releases the transaction reference after success or bounded retries.

`monitorClientDBInfoChange()` keeps snapshots of current commit and GRV proxy vectors. On changes it may launch old-proxy GRV validation, updates snapshots, clears storage-server version-vector cache because a recovery may invalidate prior commit-version data, and triggers `proxiesChangeTrigger`.

## State and persistence behavior

Most state is process-local:

- `watchMap`, `watchCounterMap`, `outstandingWatches`, and `maxOutstandingWatches` track client watch lifecycle.
- `tssMapping`, `tssMetrics`, `queueModel`, and `tssMismatchStream` track TSS request duplication and mismatch handling.
- `server_interf` interns `StorageServerInfo` objects and must be emptied or detached on context destruction.
- `cachedReadVersion`, `lastGrvTime`, and optionally `DatabaseSharedState::grvCacheSpace` hold GRV cache state.
- `ssidTagMapping` and `ssVersionVectorCache` are local caches of storage-server tag/version data.
- `healthMetrics`, `healthMetricsLastUpdated`, and `detailedHealthMetricsLastUpdated` cache health metrics.
- `clientStatusUpdater` queues serialized status payloads and owns its writer actor.
- Numerous `Counter` and `DDSketch` members accumulate telemetry until `databaseLogger()` and `tssLogger()` flush and clear samples.

Persistent cluster state is touched through transactions and system key ranges:

- Client transaction profiling data is persisted under `fdbClientInfoPrefixRange` with `client_latency/` entries and a `client_latency_counter/` byte counter.
- TSS mismatch/quarantine handling writes `tssMappingKeys`, `tssMismatchKeys`, `tssQuarantineKeyFor()`, and `serverTagKeyFor()` related system keys.
- Special-key implementations expose and, for management/configuration modules, mutate system state through their own implementation classes registered here.

## Dependencies and integration points

This file sits at the center of fdbclient. It depends on `NativeAPI.actor.h`, `DatabaseContext.h`, transaction classes, `ClusterInterface`, GRV and commit proxy interfaces, `StorageServerInterface`, `SpecialKeySpace`, `GlobalConfig`, key-backed maps, system key definitions, tracing, flow actors/futures, locality data, and client knobs. It integrates with the load balancer through `queueModel`, with server recovery metadata through `ClientDBInfo`, with client APIs through `Database`/`Transaction`, with status JSON through `getJSON()`, and with special key-space modules for management, metrics, configuration, tracing, actor lineage, profiler configuration, worker interfaces, connection strings, cluster ID, and transaction conflict introspection.

The TSS path integrates storage-server RPC endpoint tokens with test storage server endpoints. The health metrics path integrates `GrvProxyInterface::getHealthMetrics`. The client status path depends on `GlobalConfig` keys `fdbClientInfoTxnSampleRate` and `fdbClientInfoTxnSizeLimit`, plus knobs for payload and transaction byte limits.

## Risks and edge cases

- Lifetime cycles are a recurring risk. Comments call out why `clientStatusUpdateActor()` takes a raw `DatabaseContext*`, why `Transaction` objects are reset, and why watch futures are manually cancelled when the last reference disappears.
- `StorageServerInfo::getInterface()` mutates an interned `StorageServerInterface` in place when locality is unchanged. The comment notes that load balancing holds pointers into interface members, making this technically correct but unnatural and fragile.
- Version-vector logic asserts in simulation when a read version is newer than the version-vector maximum, but production avoids returning stale commit versions. Incorrect GRV-cache flags could suppress useful latest-commit-version data.
- Client status persistence relies on byte accounting through a counter updated by atomic add operations. Bugs in key/value size accounting or versionstamped-key layout could make cleanup delete too much or too little profiling data.
- TSS mismatch handling gives up after bounded retries, so persistent transaction failures can leave mismatch evidence/quarantine state unwritten until another mismatch or operator action.
- `removeTssMapping()` erases `tssMetrics` by the storage-server ID even though `addTssMapping()` stores metrics by TSS ID; this deserves caution when changing this code because an ID mismatch could leave stale metric entries.
- The AWS or special-key dependencies are not in this file, but constructor registration means API-version gates and deprecation gates are observable client behavior.
- Health metrics output returns empty under `CLIENT_BUGGIFY`, and detailed metrics are only refreshed when detail-specific staleness requires it.

## Test signals

There are no `TEST_CASE` blocks in this file. Test coverage is likely through NativeAPI, special key-space, client status, status JSON, TSS simulation, recovery, and transaction tests elsewhere. Useful test signals for changes here include watch cancellation/reference-count tests, GRV cache monotonicity tests, proxy recovery simulation that exercises `attemptGRVFromOldProxies()`, TSS mismatch quarantine/kill simulation, special key-space API-version compatibility tests, and client transaction profiling size-limit cleanup tests.
