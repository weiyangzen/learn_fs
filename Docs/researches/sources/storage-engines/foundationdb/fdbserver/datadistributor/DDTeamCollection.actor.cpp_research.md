# Research: sources/storage-engines/foundationdb/fdbserver/datadistributor/DDTeamCollection.actor.cpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008465`: lines 1-6285, `Docs/researches/chunks/subset-b-008465_research.md`
- `subset-b-008466`: lines 6286-7221, `Docs/researches/chunks/subset-b-008466_research.md`

## Chunk Research

### subset-b-008465: lines 1-6285

# sources/storage-engines/foundationdb/fdbserver/datadistributor/DDTeamCollection.actor.cpp lines 1-6285

## Scope

This chunk covers the main implementation of FoundationDB's `DDTeamCollection` for `fdbserver/datadistributor`, from includes and helper counters through the core private actor implementation, public `DDTeamCollection` forwarding methods, team/server/machine mutation helpers, perpetual storage wiggle, storage recruitment, TSS pairing, metadata updates, and the beginning of `DDTeamCollectionUnitTest`. The requested range ends at line 6285 inside `DDTeamCollectionUnitTest::testTeamCollection()` setup; the rest of the unit-test class is outside this chunk.

## Purpose

`DDTeamCollection` maintains the in-memory view of storage servers, storage teams, machine teams, health state, exclusions, and recruitment state for one data-distribution region/DC. It answers `GetTeamRequest`s from the data distributor, builds and removes teams, tracks when teams become unhealthy, emits `RelocateShard` requests for affected shards, and coordinates server lifecycle events such as storage recruitment, TSS recruitment, failed-server removal, wrong-store-type migration, and perpetual storage wiggle.

The implementation is actor-heavy. A small public class delegates most asynchronous behavior to `DDTeamCollectionImpl`, which owns static actor functions receiving a raw `DDTeamCollection*`. The public methods mostly preserve the external API declared in `DDTeamCollection.h`, while the implementation class avoids exposing actor-internal helpers in the header.

## Important APIs, Types, and Functions

- `data_distribution::EligibilityCounter` converts `GetTeamRequest` preferences into bitmask-like eligibility classes (`LOW_DISK_UTIL`, `LOW_CPU`) and tracks consecutive eligibility counts used by team selection.
- Static `TxnCounters` helpers create named counters for storage wiggle and metadata transaction loops: `/dd/updateNextWigglingStorageID`, `/dd/perpetualStorageWiggler`, `/dd/waitHealthyZoneChange`, and `/dd/updateStorageMetadata`.
- `DDTeamCollectionImpl::getTeam()`, `getTeamForBulkLoad()`, `getBestTeam()`, and `getBestTeamFromCandidates()` implement team selection for normal relocation, complete-source preservation, storage-queue-aware selection, shard-count limits, lower disk/CPU utilization preferences, bulk load balancing, and large-team custom replication.
- `DDTeamCollectionImpl::buildTeams()`, `DDTeamCollection::addTeamsBestOf()`, `addBestMachineTeams()`, `addTeam()`, and `addMachineTeam()` build balanced server teams through machine teams. They use least-used server/machine choices, randomized best-of attempts, overlap penalties, and `LocalitySet::selectReplicas()` against the configured replication policy.
- `teamTracker()` monitors one `TCTeamInfo`, derives healthy/optimal/wrong-configuration state, updates `healthyTeamCount`, `optimalTeamCount`, priority counters, and `zeroHealthyTeams`, and sends `RelocateShard` requests for shards affected by team degradation.
- `storageServerTracker()` monitors one `TCServerInfo` or TSS. It evaluates undesired status from version lag, duplicate address, process class, wrong DC, invalid locality, wrong store type, exclusions, wiggle state, and failure state; handles interface/locality changes; updates storage metadata; and removes servers when failure plus data removal completes.
- `storageServerFailureTracker()` wraps `IFailureMonitor`, `waitFailureClientStrict()`, maintenance-zone semantics, disabled-failure handling, and `waitForAllDataRemoved()` to drive `ServerStatus::isFailed` and eventual removal.
- `storageRecruiter()` and `initializeStorage()` request workers from cluster controller via `RecruitStorageRequest`, initialize storage through `InitializeStorageRequest`, avoid duplicate address recruitment, choose store types for normal/perpetual/TSS modes, and coordinate paired SS/TSS recruitment through `TSSPairState`.
- `monitorStorageServerRecruitment()` only publishes traced recruitment state transitions, including whether the active recruitment mode is TSS.
- `trackExcludedServers()` mirrors `ExclusionTracker` state into the collection's `excludedServers` map, preserving local WIGGLING entries and triggering recruitment restarts.
- `waitHealthyZoneChange()` watches `healthyZoneKey`, decodes maintenance-zone values, handles the special `ignoreSSFailuresZoneString`, clears expired zones, and updates the local `healthyZone` `AsyncVar`.
- Perpetual wiggle actors include `monitorPerpetualStorageWiggle()`, `perpetualStorageWiggler()`, `perpetualStorageWiggleIterator()`, `perpetualStorageWiggleRest()`, `clusterHealthCheckForPerpetualWiggle()`, `updateNextWigglingStorageID()`, `readStorageWiggleMap()`, `excludeStorageServersForWiggle()`, and `includeStorageServersForWiggle()`.
- `updateStorageMetadata()` writes `StorageMetadataType` records under `serverMetadataKeys`, preserves existing `createdTime`, updates `serverMetadataChangeKey`, validates sharded RocksDB metadata support, and registers the server with `StorageWiggler`.
- Public forwarding methods (`run`, `init`, `getTeam`, `buildTeams`, `teamTracker`, `storageServerTracker`, `machineTeamRemover`, `serverTeamRemover`, etc.) map the external `DDTeamCollection` API onto `DDTeamCollectionImpl`.
- Mutation helpers (`addServer`, `removeServer`, `removeTSS`, `removeTeam`, `removeMachine`, `removeMachineTeam`, `checkAndCreateMachine`, `checkAndCreateMachineTeam`) keep `server_info`, `server_and_tss_info`, `tss_info_by_pair`, `teams`, `teamsByServerIDs`, `badTeams`, `largeTeams`, `machine_info`, `machineTeams`, per-server team lists, and locality maps consistent.
- Diagnostic helpers (`traceTeamCollectionInfo`, `printSnapshotTeamsInfo`, `traceAllInfo`, `evaluateTeamQuality`, `noHealthyTeams`) produce structured trace events for production debugging and simulation assertions.
- Large-team helpers (`buildLargeTeam`, `cleanupLargeTeams`, `fixUnderReplication`, `fixUnderReplicationLoop`, `maxLargeTeamSize`) support custom per-range replication factors larger than the configured storage team size.
- Safety/status helpers include `waitUntilHealthy()`, `allServersHaveMinAvailableSpace()`, `loadBytesBalanceRatio()`, `numSSToBeLoadBytesBalanced()`, `isValidLocality()`, `shouldHandleServer()`, `findTeamFromServers()`, `teamContainsFailedServer()`, and `exclusionSafetyCheck()`.

## Control Flow

Startup flows through `DDTeamCollection::run()`. It calls `init()` to load existing storage servers and teams from `InitialDataDistribution`, starts `serverGetTeamRequests()`, waits for `readyToStart`, starts bad-team cleanup, team removers, large-team repair when enabled, wrong-store-type cleanup, replica-key updates, healthy-team monitoring, and, for real databases, recruitment, server-list polling, exclusion tracking, healthy-zone watching, and perpetual wiggle monitoring. Its main loop then reacts to removed SS/TSS notifications, zero-healthy-team transitions, periodic data-in-flight logging, server tracker errors, and actor-collection failures.

Initialization uses `shouldHandleServer()` to filter storage servers for the collection's included or tracked DCs. Invalid locality is recorded in `invalidLocalityAddr` and monitored by `checkAndRemoveInvalidLocalityAddr()`, which polls workers until locality is corrected or the address disappears. Existing primary or remote teams are inserted through `addTeam()`, which classifies them as healthy teams, bad teams, or large teams depending on policy and size.

Team selection starts when `serverGetTeamRequests()` receives a `GetTeamRequest`. Exact lookup uses `teamsByServerIDs`. Bulk load selection waits for team building, filters healthy eligible teams that do not overlap source servers, samples candidates with a power-of-D-choice ratio, then minimizes the maximum current bulk-load task count over destination servers. Normal selection waits for build completion, handles not-ready remote DCs by returning an existing source team, updates CPU/disk pivots, optionally builds a large team for custom replication, honors `WANT_COMPLETE_SRCS`, computes storage-queue thresholds when requested, and either scans all teams for true best or samples random candidates. If storage-queue-aware or moveout true-best selection finds no team, it retries with those constraints disabled.

Team construction is two-layered. `addBestMachineTeams()` first builds machine teams using `machineLocalityMap` and the configured replication policy, preferring least-used healthy machines and avoiding duplicate machine-team overlaps. `addTeamsBestOf()` then chooses a least-used healthy server, picks a healthy machine team containing its machine, selects one healthy server from each machine, penalizes overlap with existing server teams, and adds the lowest-score candidate. `buildTeams()` decides how many teams to build from desired/max teams per server, current healthy/non-wrong-configuration teams, and enough-machine checks; if it cannot build due to too few unique machines or no candidates, it records `lastBuildTeamsFailed`.

Team health tracking is edge-triggered. Each `teamTracker()` computes failed/undesired/wrong-configuration/wiggling counts, marks the team healthy only when it is not bad, has no undesired members, and all members are left, updates healthy and optimal counters, recalculates relocation priority, and sends `RelocateShard` for all shards known to `ShardsAffectedByTeamFailure` when the initial failure delay has elapsed and there is at least one healthy team or the team contains a failed server. It also checks related primary/remote teams for the same shard to choose the maximum priority across all affected teams.

Server tracking is the main status fan-in. `storageServerTracker()` loops over current server metadata, recomputes undesired and wrong-configuration flags, subscribes to exclusion, class, lag, queue, wrong-store-type, and interface-change events, starts `storageServerFailureTracker()`, and waits on a `choose` block. Removal happens only after failure tracking observes the server unhealthy and `waitForAllDataRemoved()` completes, at which point the database removes the server and the collection later handles `removeServer()` or `removeTSS()`. Interface changes can update last-known interface/class, rebuild machine membership on zone changes, invalidate teams that no longer satisfy policy, restart metadata tracking, and trigger team building or recruitment.

Recruitment is demand-driven and debounced by `restartRecruiting`. `storageRecruiter()` computes exclusions from existing unhealthy/undesired/wiggling servers, in-progress recruitment localities, configured exclusions, failed addresses, and invalid-locality workers. It asks cluster controller for a candidate worker, decides whether to recruit a TSS or normal SS based on desired TSS count and current healthy teams, and delegates the worker to `initializeStorage()`. `initializeStorage()` prevents more than two storage servers per address, inserts the in-progress ID/locality before awaiting RPCs, chooses the proper store type, sends `InitializeStorageRequest`, waits for SS/TSS pairing when needed, adds successful servers to the collection, and always decrements `recruitingStream` and retriggers recruitment.

Perpetual storage wiggle watches `perpetualStorageWiggleKey`. When enabled, it restores wiggle stats and starts an iterator plus a wiggler actor. The iterator waits for each completed wiggle, enforces rest conditions, then persists the next wiggling server ID. The wiggler restores any persisted current ID, waits until the cluster is healthy and not paused, excludes the selected server as `WIGGLING`, waits for removal/data movement, clears the metadata map, includes wiggle exclusions again, and advances to the next ID. Health checking pauses wiggle when unhealthy relocation count is high, healthy team count is too low, or best-team selection has been stuck.

Team and machine removal actors periodically wait until the collection is healthy and then reduce excess teams. `machineTeamRemover()` removes machine teams above the desired count, reclassifying their server teams as redundant bad teams before deleting the machine team. `serverTeamRemover()` similarly marks overrepresented server teams as redundant when total teams exceed the desired count by the configured threshold. `removeBadTeams()` waits until the collection is stable and the emergency subset pass has completed, then cancels and clears bad-team trackers.

Removal cleanup is explicit. `removeServer()` removes the server from `StorageWiggler`, per-server shared team lists, `teams`, `badTeams`, `largeTeams`, the machine's server list, empty machine records, `allServers`, `server_info`, `server_and_tss_info`, `server_status`, and the locality set, then schedules team rebuilding. `removeTSS()` only removes TSS-specific indexes because TSSs are not members of data teams.

## State and Persistence Behavior

- Long-lived in-memory collection state includes `server_info`, `server_and_tss_info`, `tss_info_by_pair`, `allServers`, `server_status`, `teams`, `teamsByServerIDs`, `badTeams`, `largeTeams`, `machine_info`, `machineTeams`, `machineLocalityMap`, `storageServerSet`, `excludedServers`, `invalidLocalityAddr`, `recruitingIds`, `recruitingLocalities`, `wiggleAddresses`, `wigglingId`, `teamPivots`, `underReplication`, and counters for healthy/optimal teams and unhealthy servers.
- `teamsByServerIDs` is an in-memory exact lookup index for normal teams. It is updated in `addTeam()` and erased in `removeTeam()`. Simulation-only consistency checks compare it against `teams`.
- `server_status` is an `AsyncMap`-style status source watched by team trackers, server trackers, and removers. It persists no data itself, but drives relocation priorities and recruitment exclusions.
- `healthyZone` is populated from the persistent `healthyZoneKey`. Maintenance-zone state affects failure tracking: failures in the healthy zone are ignored, and the special ignore-all value disables SS failure handling until cleared.
- `updateReplicasKey()` persists the configured replica count for a DC using `tryUpdateReplicasKeyForDc()` after all initial servers have reported updated and the collection is healthy.
- `updateStorageMetadata()` persists per-storage metadata under `serverMetadataKeys`, preserving the original created time when present, setting the observed store type and wrong-store-type marker, and writing `serverMetadataChangeKey` to notify observers.
- Perpetual wiggle persists the current or next wiggling server through `StorageWiggleData::wigglingStorageServer()`. It also stores accumulated delay when the configured wiggle delay exceeds one minute, allowing long delays to survive actor restarts.
- Storage recruitment persists new storage servers indirectly through worker `InitializeStorageRequest` handling and `db->removeStorageServer()` cleanup for removals. The collection then mirrors server-list state in memory.
- TSS state is mostly in-memory in this chunk (`tss_info_by_pair`, `TSSPairState`, kill promises, pair removal futures), but it relies on storage server interfaces containing `tssPairID` and added versions from recruitment.
- `underReplication` is an in-memory range map used to retry relocation for ranges requiring larger custom replication teams. It is updated from `getTeam()` and `fixUnderReplication()`.
- `StorageWiggler` state combines in-memory queue/stat tracking with persisted wiggle metadata. Servers are added, updated, or removed as storage metadata changes and server lifecycle events occur.

## Dependencies and Integration Points

- Flow actor runtime: `ACTOR`, coroutine actors, `Future`, `Promise`, `PromiseStream`, `FutureStream`, `choose`, `wait`, `waitNext`, `race`, `timeout`, `quorum`, `actorCollection`, `SignalableActorCollection`, `AsyncVar`, `TaskPriority`, and actor cancellation semantics are central.
- Data distribution contracts: `TeamCollectionInterface`, `GetTeamRequest`, `IDataDistributionTeam`, `RelocateShard`, `RelocateReason`, `ShardsAffectedByTeamFailure`, `InitialDataDistribution`, `DDEnabledState`, `DDTxnProcessor`, and `MoveKeysLock` connect this collection to the wider data distributor and DD queue.
- Team/server model types: `TCServerInfo`, `TCTeamInfo`, `TCMachineInfo`, `TCMachineTeamInfo`, `ServerStatus`, `TSSPairState`, `StorageWiggler`, and `BulkLoadTaskCollection` are the core local model dependencies.
- Replication policy and locality: `LocalityData`, `LocalityMap`, `LocalitySet`, `LocalityEntry`, `IReplicationPolicy`, `AddressExclusion`, `includedDCs`, `otherTrackedDCs`, and `ProcessClass` decide whether servers and teams are valid for this collection.
- Cluster controller and storage worker RPCs: `RecruitStorageRequest`, `RecruitStorageReply`, `InitializeStorageRequest`, and `InitializeStorageReply` provide the recruitment path.
- Failure and server-list monitoring: `IFailureMonitor`, `waitFailureClientStrict()`, `db->getServerListAndProcessClasses()`, `db->removeStorageServer()`, `db->getWorkers()`, and server-interface change promises keep live state synchronized with worker and server-list reality.
- System keys and key-backed metadata: `healthyZoneKey`, `perpetualStorageWiggleKey`, `serverMetadataKeys`, `serverListKeyFor()`, `serverMetadataChangeKey`, `StorageWiggleData`, `StorageWiggleValue`, `StorageMetadataType`, and `KeyBackedObjectMap` provide the persistent administrative state.
- Configuration and knobs: behavior is heavily controlled by `SERVER_KNOBS`, `FLOW_KNOBS`, `DatabaseConfiguration`, storage migration mode, store types, TSS desired count, team sizing, best-of attempts, remover delays, disk/CPU pivots, storage queue thresholds, wiggle pause thresholds, and simulation-only knobs.
- Observability: `TraceEvent`, `EventCacheHolder::trackLatest`, `CODE_PROBE`, `TxnCounters`, severity levels, and print-snapshot triggers are deeply interleaved with state transitions.
- Bulk load integration: `getTeamForBulkLoad()` consults `bulkLoadTaskCollection->busyMap` to choose a destination team with fewer active bulk-load tasks.
- Custom replication integration: `userRangeConfig` and large-team support interact with range configuration to create teams larger than `configuration.storageTeamSize` when a key range asks for a larger replication factor.

## Risks and Edge Cases

- Team indexes must stay consistent. `teams`, each server's team vector, `teamsByServerIDs`, `machineTeam->serverTeams`, and tracker lifetimes are updated manually in several paths. A missed erase or stale tracker could cause wrong team lookup, duplicate relocation, or use-after-destruction.
- `teamTracker()` has cross-collection references through `teamCollections`. The destructor explicitly nulls peer pointers because trackers can react after one collection has been destroyed.
- The team-health counters are incrementally maintained. Incorrect first-check handling, cancellation accounting, or healthy/optimal transitions could make `zeroHealthyTeams` or `zeroOptimalTeams` inaccurate, blocking recruitment or causing unsafe team selection.
- Server locality changes are complex. Zone changes require removing a server from one machine, adding it to another, potentially creating/removing machine teams, marking teams bad, and rebuilding locality maps. The code intentionally leaves some representative locality entries stale until rebuild, which is safe only if callers know when to rebuild.
- `addTeam()` marks bad teams before adding them to normal indexes. Bad teams still have trackers and can relocate data; cleanup relies on `removeBadTeams()` after stability. Races between bad-team creation and remover are explicitly mitigated by waiting on `badTeamRemover`.
- Team building uses randomized best-of attempts and overlap penalties. It can fail under too few machines, invalid locality, many duplicate teams, or missing machine teams, setting `lastBuildTeamsFailed`; downstream logic uses this flag to retrigger building.
- Storage queue aware team selection can filter every team. The fallback recursion disables `storageQueueAware` and `wantTrueBestIfMoveout`, but the trace logs detail the old flags after they have already been changed, which can make diagnostics confusing.
- Bulk load team selection uses eligibility counters and random simulation bypass for low-disk checks. This prevents some simulation deadlocks but means simulation behavior differs from production.
- The invalid-locality cleanup loop erases from `invalidLocalityAddr` and then traces the erased iterator's value in one branch (`addr = erase(addr)` followed by `addr->toString()`), which would be unsafe if reached as written.
- Perpetual wiggle safety depends on correct interaction between exclusions, `wigglingId`, persisted wiggle map, `pauseWiggle`, `waitUntilRecruited`, and recruitment. Overwriting real operator exclusions is avoided, but abnormal preexisting exclusion states cause wiggle exclusion to no-op.
- Wrong-store-type removal is intentionally delayed until healthy and only acts aggressively in aggressive migration mode. In gradual mode it may only log and rely on perpetual wiggle, so store-type convergence depends on wiggle configuration.
- `storageServerTracker()` may throw `movekeys_conflict()` after failed exclusions to force DD restart/removal behavior. This is a high-impact control path and depends on `ddEnabledState` eventually enabling.
- TSS recruitment is stateful and timing-sensitive. The SS side may time out waiting for TSS, TSS recruitment may be canceled when desired count falls or zero healthy teams appear, and kill logic iterates `tss_info_by_pair` while server trackers can remove entries.
- Persistent metadata writes use RYW transactions with system-key access and retry loops. Missing server-list entries cause `updateStorageMetadata()` to return `Never()`, intentionally keeping the caller actor inert for a removed server.
- `waitUntilHealthy()` can wait indefinitely when zero healthy teams, unhealthy processing, or wiggle processing remain true. Many removers and migration actions are intentionally gated behind this, so incorrect flags can stall cleanup.
- `exclusionSafetyCheck()` only checks remaining replica count per existing team against `DD_EXCLUDE_MIN_REPLICAS`; it does not by itself validate all policy/locality dimensions for post-exclusion placement.
- The chunk ends after unit-test setup begins, so detailed unit-test coverage and any static test cases below line 6285 must be analyzed by a later chunk.

## Test Signals

- Team selection tests should cover exact team lookup through `teamsByServerIDs`, normal best-team selection, true-best scans, random candidate selection, storage-queue-aware filtering and fallback, shard-count-limit preferences, zero-healthy-team source fallback, complete-source preservation, and lower disk/CPU eligibility counters.
- Bulk load tests should cover overlap avoidance with source servers, unhealthy/ineligible filtering, power-of-D candidate sampling, per-server busy-count minimization, and failure to find any valid team.
- Team-building tests should cover enough/insufficient unique machines, invalid locality, machine-team prebuilds, least-used server selection, overlap penalties, duplicate team avoidance, target team count invariants, `lastBuildTeamsFailed`, and simulation consistency of `teamsByServerIDs`.
- Team tracker tests should cover priority changes for 0/1/2 servers left, undesired/wrong-configuration/wiggling servers, redundant bad teams, zero healthy/optimal counters, initial failure reaction delay, ignored SS failures during healthy-zone mode, and emitted `RelocateShard` priority for shards mapped to multiple primary/remote teams.
- Server tracker tests should cover version-lag undesired state, duplicate address selection, wrong machine class, wrong DC, invalid locality, wrong store type, excluded/failed/wiggling addresses including secondary addresses, interface and locality changes, long storage queue rebalance triggers, and removal after `waitForAllDataRemoved()`.
- Recruitment tests should cover critical recruitment when no healthy team exists, address exclusions, invalid-locality exclusions, in-progress locality suppression, maximum storage servers per address, store type choice for normal/perpetual/TSS recruitment, request-maybe-delivered handling, and recruitment stream state transitions.
- TSS tests should cover target distribution across usable regions, TSS/SS pairing success, pair timeout, cancellation when over target, cancellation or kill when zero healthy teams, pair server removal waking TSS tracker, and `tss_info_by_pair` cleanup.
- Perpetual wiggle tests should cover enabling/disabling through `perpetualStorageWiggleKey`, persisted current ID restoration, locality-filtered selection, pause/resume on cluster health, rest conditions for load imbalance and low available space, exclusion/inclusion behavior, metadata map erase, and interactions with recruitment.
- Metadata persistence tests should cover `updateReplicasKey()`, storage metadata creation and update preserving `createdTime`, absent server-list no-op, wrong-store-type detection, sharded RocksDB physical-shard knob validation, `serverMetadataChangeKey` updates, and `StorageWiggler` add/update/remove behavior.
- Maintenance-zone tests should cover healthy-zone start, timeout, manual clear, ignore-all-SS-failures value, failure tracker suppression within the healthy zone, and optional maintenance-zone clearing on failure.
- Removal tests should cover `removeTeam()`, redundant team cleanup, bad/large team removal, server removal from all indexes, empty machine removal, machine team cleanup, TSS-only removal, locality set reset, and restarting team building/recruitment after removals.
- Large-team tests should cover custom range replication factors, too few healthy servers, maximum shards on large teams, cleanup of unused large teams, under-replication range marking, and relocation retry after larger teams become available.
- Diagnostics and simulation tests should verify trace snapshots, team quality events, `NoHealthyTeams`, `DataDistributionTeamCollectionUpdate`, simulated `CODE_PROBE`s, consistency checks for team indexes, and bounded yielding in `printSnapshotTeamsInfo()`.

### subset-b-008466: lines 6286-7221

# sources/storage-engines/foundationdb/fdbserver/datadistributor/DDTeamCollection.actor.cpp lines 6286-7221

## Scope

This chunk is the end of `DDTeamCollection.actor.cpp`. It starts in the tail of the `DDTeamCollectionUnitTest::testTeamCollection(...)` fixture helper, covers the rest of the `DDTeamCollectionUnitTest` class, and ends with the `TEST_CASE` registrations for data-distribution team construction, team selection, storage wiggler ordering, TSS-aware wiggle selection, CPU cutoffs, and shard-count-aware destination preference. The production implementation of `DDTeamCollection`, `TCTeamInfo`, `TCServerInfo`, `StorageWiggler`, and `DDTeamCollectionImpl::getNextWigglingServerID()` is earlier in the file; this chunk exercises those APIs rather than defining their main behavior.

## Purpose

The code builds small synthetic `DDTeamCollection` instances and verifies critical destination-team selection invariants used by FoundationDB data distribution:

- Team construction should respect replication policy, locality, team-size limits, and per-server coverage goals.
- `addTeamsBestOf()` should create enough healthy server teams without duplicating invalid combinations and should still give every server at least one team in constrained clusters.
- `getTeam()` should honor complete-source preference, unhealthy-team avoidance, disk utilization preference, minimum free-space cutoffs, read-bandwidth balancing, paused-wiggle deprioritization, CPU destination cutoffs, and optional shard-count limits.
- `StorageWiggler` should pick storage servers in the intended order based on store type, age, TSS needs, and metadata updates.

The tests serve as a regression net for data movement target choice. Failures here usually imply a behavioral change in data-distribution safety, balance, or recruitment/wiggle logic.

## Important APIs, Types, and Functions

- `DDTeamCollectionUnitTest::testTeamCollection(...)`: creates a test `DatabaseContext`, `DDTxnProcessor`, `DatabaseConfiguration`, and `DDTeamCollection`, then inserts synthetic `StorageServerInterface` objects into `server_info` and `server_status`. In the visible tail of the helper, each server receives `machineid`, `zoneid`, and `data_hall` locality and immediately calls `checkAndCreateMachine()`.
- `DDTeamCollectionUnitTest::testTeamCollection(int, Reference<IReplicationPolicy>, int)`: convenience overload that allocates a fresh `ShardsAffectedByTeamFailure`.
- `DDTeamCollectionUnitTest::testMachineTeamCollection(...)`: fixture variant that derives hierarchical locality from the numeric process id (`dcid`, `data_hall`, `zoneid`, `machineid`, `processid`), populates `server_info` and `server_status`, then calls `constructMachinesFromServers()`.
- `PolicyAcross` and `PolicyOne`: replication-policy fixtures used to require placement across `zoneid` for most multi-replica tests, or no locality constraint for single-replica tests.
- `DDTeamCollection::addBestMachineTeams()`, `addTeamsBestOf()`, `addTeam()`, `sanityCheckTeams()`, `disableBuildingTeams()`, `setCheckTeamDelay()`, `getTeam()`: the primary production APIs under test.
- `GetTeamRequest`: constructed with `TeamSelect` (`WANT_COMPLETE_SRCS`, `WANT_TRUE_BEST`, `ANY`) plus preference flags (`PreferLowerDiskUtil`, `TeamMustHaveShards`, `PreferLowerReadUtil`, `PreferWithinShardLimit`, `ForReadBalance`). The tests fill `completeSources` where source-awareness matters and read results from `req.reply`.
- `GetStorageMetricsReply` and `HealthMetrics::StorageStats`: synthetic server metric inputs for disk capacity, available bytes, storage load, read bandwidth, read ops, and CPU usage.
- `ShardsAffectedByTeamFailure`: injected into one fixture to assign many key ranges to a specific team and verify shard-count avoidance.
- `StorageWiggler`, `StorageMetadataType`, `KeyValueStoreType`, and `DDTeamCollectionImpl::getNextWigglingServerID()`: exercised by the final storage-wiggler tests.
- `TEST_CASE(...)`: Flow test registrations that expose these helpers to the FoundationDB unit-test runner.

## Control Flow

The fixture setup follows two patterns. The simple helper constructs the collection and, for each synthetic server id, installs a `StorageServerInterface`, locality entries, a `TCServerInfo`, and a healthy `ServerStatus`; this chunk includes the final locality and machine creation operations before returning the collection. The machine-aware helper performs the same core setup but derives locality buckets from integer divisions of the process id and builds all machine structures in one pass via `constructMachinesFromServers()`.

The team-building tests first create a policy and collection, then call `addTeamsBestOf()` or `addBestMachineTeams()` with desired and maximum counts derived from `SERVER_KNOBS`. `AddTeamsBestOf_UseMachineID` and `AddTeamsBestOf_NotUseMachineID` validate that machine-aware and prebuilt-machine-team paths can generate sane server teams. `AddAllTeams_isExhaustive` asks for more teams than possible and asserts the exact locality-valid count of 80. `AddAllTeams_withLimit` asks for 10 and accepts any result at or above that limit. The constrained-server tests seed two teams manually, build more, and assert every server is covered; `NotEnoughServers` also asserts exactly 10 machine teams and 8 added server teams after debugging output if the expectations fail.

The `getTeam()` tests all disable background team building and set the check-team delay so the request result reflects the manually constructed test universe. They then populate metrics and call `co_await collection->getTeam(req)`. `WANT_COMPLETE_SRCS` tests verify that a healthy complete-source team is reused when possible and that an unhealthy team is skipped in favor of another team composed only of complete sources. `WANT_TRUE_BEST` tests compare lower-disk-utilization versus higher-utilization selection, reject teams whose members are below minimum space thresholds, and reject near-cutoff teams when the ratio threshold is the controlling limit.

Read balancing and CPU filtering are tested with single-replica teams. The read-bandwidth test issues two requests concurrently: one that prefers low read utilization and one that does not. It expects the low-read request to pick server 4, the high-utilization request to pick server 5, then adds in-flight read penalty to the first selected team and expects the next low-read selection to move to server 2. The CPU cutoff test forces stale pivot values, optionally changes the `cpu_pivot_ratio` knob, creates four single-server teams with combinations of high/low space, high/low read, and low/mid/high CPU, then verifies the best team is server 2 and any random candidate excludes the low-space and high-CPU servers.

The shard-count preference test populates `ShardsAffectedByTeamFailure` with more than `DESIRED_MAX_SHARDS_PER_TEAM` randomly generated adjacent ranges assigned to the first team. With `PreferWithinShardLimit::True`, `getTeam()` must pick the second team regardless of whether the request uses `WANT_TRUE_BEST` or `ANY`.

The final `TEST_CASE` blocks register each helper. Most actor helpers are wrapped in `wait(...)`; synchronous helpers are called directly. The storage-wiggler tests are inline `TEST_CASE` bodies: one checks age/type ordering and future completion after metadata update, and the other checks TSS-sensitive wiggle selection against a one-replica machine-aware collection.

## State and Persistence Behavior

All state in this chunk is synthetic in-memory test state. The fixture creates a `DatabaseContext` and `DDTxnProcessor`, but the tests do not persist user data or commit transactions. Instead, they mutate `DDTeamCollection` internals that model data-distribution state:

- `server_info` maps UIDs to `TCServerInfo` objects carrying interfaces, metrics, storage stats, and team membership.
- `server_status` tracks healthy, desired, non-wiggling server status plus locality.
- `machine_info`, machine teams, and machine locality maps are created incrementally by `checkAndCreateMachine()` or in bulk by `constructMachinesFromServers()`.
- `teams`, `teamsByServerIDs`, and per-server team vectors are populated by `addTeam()` and `addTeamsBestOf()`.
- `machineTeams` is populated by `addBestMachineTeams()` and indirectly used by `addTeamsBestOf()` when constructing server teams.
- `pauseWiggle`, `wigglingId`, and `configuration` fields are directly modified in tests for paused-wiggle and TSS cases.
- `teamPivots` and server CPU stats feed candidate filtering in the CPU cutoff test.
- `ShardsAffectedByTeamFailure` stores key-range-to-team assignments for the shard-count limit test.
- `StorageWiggler` stores server metadata and pending notification state; `getNextWigglingServerID()` waits until an eligible server exists.

The durable behavior being protected is indirect: these tests verify that production data-distribution state transitions would choose safe relocation destinations and storage wiggle candidates under the same metrics and topology conditions.

## Dependencies and Integration Points

- Flow actor/test infrastructure: `Future<Void>`, `co_await`, `wait`, `success`, `trigger`, `delay`, `state`, and `TEST_CASE` integrate with FoundationDB's deterministic simulation test runner.
- Data-distribution types: `DDTeamCollection`, `DDTeamCollectionInitParams`, `DDTxnProcessor`, `MoveKeysLock`, `RelocateShard`, `GetMetricsRequest`, `RebalanceStorageQueueRequest`, `BulkLoadTaskCollection`, `TCServerInfo`, `TCTeamInfo`, and `TCMachineTeamInfo`.
- Locality and replication policy: `LocalityData`, `StorageServerInterface::locality`, `PolicyAcross`, `PolicyOne`, and `IReplicationPolicy` determine whether a team satisfies placement rules.
- Server knobs: `DESIRED_TEAMS_PER_SERVER`, `MAX_TEAMS_PER_SERVER`, `MIN_AVAILABLE_SPACE`, `MIN_AVAILABLE_SPACE_RATIO`, `MAX_DEST_CPU_PERCENT`, `CPU_PIVOT_RATIO`, `DESIRED_MAX_SHARDS_PER_TEAM`, `ENFORCE_SHARD_COUNT_PER_TEAM`, and `DD_STORAGE_WIGGLE_MIN_SS_AGE_SEC` shape expected outcomes.
- Metrics interfaces: `GetStorageMetricsReply` supplies capacity, availability, load bytes, read bandwidth, and read operations; `HealthMetrics::StorageStats` supplies CPU.
- Randomness: `deterministicRandom()` generates keys, chooses between request modes in one test, and decides which CPU cutoff path to exercise.
- Tracing/debugging: `printf`, `fmt::print`, `std::cout`, `traceAllInfo(true)`, and `CODE_PROBE` provide failure diagnostics and simulation coverage signals.

## Risks and Edge Cases

- The chunk begins inside `testTeamCollection(...)`; the constructor arguments and first locality entries are just before the requested start line. Research for this chunk therefore depends on that small boundary context to explain the helper correctly.
- Several tests assume exact team counts despite comments about randomness in team discovery. Deterministic simulation should make this reproducible, but changes to replica selection or machine-team balancing can legitimately alter expected counts.
- `AddTeamsBestOf_NotUseMachineID` calls `sanityCheckTeams()` without asserting the result. That makes it weaker as a regression signal than the machine-id variant.
- `GetTeam_ServerUtilizationNearCutoff` is tightly coupled to knob values and floating-point ratio behavior. If `MIN_AVAILABLE_SPACE_RATIO` or available-space cutoff semantics change, the test may fail for threshold math rather than team-selection ordering.
- `GetTeam_CutOffByCpu` mutates `cpu_pivot_ratio` on one branch and does not restore it locally. This is probably acceptable in FoundationDB knob-test infrastructure, but it is a shared-state risk if tests are reordered or run outside the expected simulation isolation.
- Tests call `disableBuildingTeams()` and `setCheckTeamDelay()` to make selection deterministic. If future `getTeam()` behavior performs additional asynchronous checks or team construction despite these controls, these tests may become flaky or stop isolating the intended behavior.
- The read-bandwidth test depends on in-flight read penalty changing the next selected team. Changes to penalty scaling, read-load comparison, or tie-breaking can invalidate the exact expected UID.
- Storage-wiggler tests use `now()`, min-age delays, and future readiness. They are simulation-friendly, but wall-clock-like behavior or altered min-age rules could make assertions fragile.
- The TSS storage-wiggler test directly edits `configuration.usableRegions` and `desiredTSSCount`; changes to `reachTSSPairTarget()` semantics can alter which server is eligible before normal min age.

## Test Signals

- `DataDistribution/AddTeamsBestOf/UseMachineID`: `addTeamsBestOf()` can build teams from machine locality and pass `sanityCheckTeams()`.
- `DataDistribution/AddTeamsBestOf/NotUseMachineID`: prebuilt machine teams plus server team building complete without null collection failure and run the sanity checker.
- `DataDistribution/AddAllTeams/isExhaustive`: across-zone replication with 10 processes and team size 3 yields exactly 80 valid teams after filtering same-zone combinations.
- `/DataDistribution/AddAllTeams/withLimit`: bounded team construction can satisfy at least the requested lower limit.
- `/DataDistribution/AddTeamsBestOf/SkippingBusyServers`: seeded busy/covered servers do not prevent adding at least 8 teams, and every server ends with at least one team.
- `/DataDistribution/AddTeamsBestOf/NotEnoughServers`: constrained five-server topology still builds all 10 machine teams, covers every server, and finds the expected 8 additional teams.
- `/DataDistribution/GetTeam/NewServersNotNeeded`: `WANT_COMPLETE_SRCS` maintains the healthy complete-source team instead of moving to higher-availability new servers.
- `/DataDistribution/GetTeam/HealthyCompleteSource`: an unhealthy complete-source team is skipped in favor of another healthy complete-source team.
- `/DataDistribution/GetTeam/TrueBestLeastUtilized` and `TrueBestMostUtilized`: the disk-utilization preference flag controls whether lower or higher utilized teams are selected.
- `/DataDistribution/GetTeam/ServerUtilizationBelowCutoff` and `ServerUtilizationNearCutoff`: teams below absolute or ratio free-space cutoffs are rejected.
- `/DataDistribution/GetTeam/TrueBestLeastReadBandwidth`: read-balancing selection honors read load and in-flight read penalty.
- `/DataDistribution/GetTeam/DeprioritizeWigglePausedTeam`: a team containing the paused wiggling server is deprioritized even when otherwise attractive.
- `/DataDistribution/StorageWiggler/NextIdWithMinAge`: storage-wiggler ordering accounts for store type, min age, special metadata flags, and asynchronous metadata updates.
- `/DataDistribution/StorageWiggler/NextIdWithTSS`: TSS target state changes eligibility and allows a younger server to be selected before the normal age deadline.
- `/DataDistribution/GetTeam/CutOffByCpu`: CPU and space candidate filtering excludes high-CPU and low-space teams for best and random selection paths.
- `/DataDistribution/GetTeam/PreferWithinShardRange`: when shard-count enforcement is enabled, selection avoids the team already above the desired shard limit.
