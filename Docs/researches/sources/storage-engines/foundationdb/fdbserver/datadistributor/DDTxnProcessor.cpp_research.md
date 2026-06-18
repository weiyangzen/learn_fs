# sources/storage-engines/foundationdb/fdbserver/datadistributor/DDTxnProcessor.cpp

## Purpose

`DDTxnProcessor.cpp` implements the real and mock transaction-processing layer used by FoundationDB data distribution. The real `DDTxnProcessor` adapts `IDDTxnProcessor` calls into system-key transactions, NativeAPI helpers, `DatabaseContext` metrics calls, and `MoveKeys` operations. The mock `DDMockTxnProcessor` implements the same surface over `MockGlobalState` so simulation workloads can compare real key-server/server-key behavior with an in-memory model.

The file is a testability boundary for data distribution. Data-distribution actors can depend on `IDDTxnProcessor` for reads, metadata mutation, movement, health, and storage metrics without directly owning transaction details everywhere. This lets production use real database transactions while test workloads exercise the same movement APIs against a deterministic mock state.

## Important APIs, Types, and Functions

- `updateServersAndCompleteSources()` accumulates all source servers covering a requested range and computes `completeSources`, the intersection of source teams across all shards in that range.
- `DDTxnProcessorImpl` contains static coroutine helpers for the real processor:
  - `getServerListAndProcessClasses()` reads the storage server list and process classes through `NativeAPI::getServerListAndProcessClasses()`.
  - `getSourceServersForRange()` reads `serverTagKeys`, `keyServers`, and sometimes `serverListKeys` to return all source servers and complete sources for a range.
  - `getSourceServerInterfacesForRange()` reads key-server ranges and resolves source `StorageServerInterface`s grouped by data center ID.
  - `updateReplicaKeys()` and `tryUpdateReplicasKeyForDc()` maintain `datacenterReplicasKeys`, including setting `rebootWhenDurableKey` when replica count increases.
  - `getHealthyZone()` reads maintenance-mode state with a bounded retry count so DD startup does not block indefinitely on a hot system shard.
  - `rewriteShardEncodedMetadata()` handles downgrade/rollback cleanup when `SHARD_ENCODE_LOCATION_METADATA` is disabled.
  - `getInitialDataDistribution()` reconstructs initial DD state from server list, workers, data moves, key-server ranges, data-center placement, and optional large-team user range config.
  - `waitForDataDistributionEnabled()`, `isDataDistributionEnabled()`, and `pollMoveKeysLock()` gate work on DD mode, transient DD enabled state, and the move-keys lock.
  - `waitDDTeamInfoPrintSignal()` watches `triggerDDTeamInfoPrintKey`.
  - `waitForAllDataRemoved()` waits until a removed server is old enough, has no server-key ownership, and has no tracked affected shards.
- `DDTxnProcessor` is the production adapter. Most methods forward to `DDTxnProcessorImpl`, global movement helpers such as `moveKeys()`, `rawStartMovement()`, `rawFinishMovement()`, and `removeStorageServer()`, or `DatabaseContext` methods such as `waitStorageMetrics()`, `splitStorageMetrics()`, `getReadHotRanges()`, `getHealthMetrics()`, and `getStorageStats()`.
- `DDMockTxnProcessorImpl` and free mock helpers implement movement over `MockGlobalState`:
  - `checkFetchingState()` waits for all destination mock servers to reach `FETCHED` or `COMPLETED`.
  - `moveKeys()` sorts teams, runs mock raw start, waits for fetch completion, runs mock raw finish, and signals `dataMovementComplete`.
  - `rawStartMovement()` defines shard boundaries, records destination teams as in-flight, computes range size, and signals fetches on destination servers.
  - `rawFinishMovement()` verifies the destination team, marks destinations completed, removes the shard from non-destination source servers, and finalizes/coalesces shard mapping.
- `DDMockTxnProcessor` also reconstructs `DDShardInfo` from mock shard mapping, populates mock state from initial real DD state, exposes mock metrics and config, and provides mock `getSourceServersForRange()` and `waitForAllDataRemoved()`.

## Control Flow

Real initial-data loading starts in `getInitialDataDistribution()`. It optionally loads large-team user range configuration, reads maintenance mode through `getHealthyZone()`, then performs a first transaction that reads DD mode, bulk load/dump modes, workers, server list, and persisted data moves. It separates TSS servers from normal storage servers, maps storage server IDs to data-center IDs, optionally rewrites shard-encoded metadata when the knob is off, decodes `DataMoveMetaData`, splits movement source/destination servers into primary and remote data-center vectors, and stores valid movements in `result->dataMoveMap`.

The second phase scans `keyServers` in batches from `allKeys.begin` to `allKeys.end`. Each batch checks the move-keys lock, reads the UID-to-tag map, decodes key-server source/destination teams, classifies teams into primary and remote regions when remote DC IDs are supplied, caches repeated team classifications, records unique teams, and appends `DDShardInfo` entries. A dummy shard at `allKeys.end` terminates the shard vector. If shard-encoded metadata is enabled and persisted moves exist, the function validates each shard against the recovered data-move map.

Source-server lookup is smaller but important for relocation. `getSourceServersForRange()` reads the key-server rows covering the requested range. When the row count fits under `DD_QUEUE_MAX_KEY_SERVERS`, it decodes each shard's source vector and accumulates all unique sources plus the intersection of complete sources. If the key-server range is too large, it conservatively returns every storage server from `serverListKeys`, because crash recovery can temporarily make many destination servers act as possible sources.

The data distribution enabled checks loop through retryable transactions. `waitForDataDistributionEnabled()` sleeps between reads and returns only when persistent mode and transient `DDEnabledState` both allow DD. `isDataDistributionEnabled()` also checks `moveKeysLockOwnerKey` so a data-distribution-mode lock owner can keep DD disabled. `pollMoveKeysLock()` continuously verifies an already-held lock through `checkMoveKeysLockReadOnly()`.

Mock movement follows the same high-level start/fetch/finish contract without real transactions. `rawStartMovement()` takes the start parallelism lock, defines necessary shard boundaries, moves the selected mock ranges to an in-flight destination team, and signals fetch work. `rawFinishMovement()` takes the finish lock, verifies the expected destination team, marks destination shards completed, removes the shard from source servers not in the destination, finishes the move in the shard mapping, and redefines the moved range to coalesce merge cases.

## State and Persistence Behavior

The production processor persists or reads only through FoundationDB system keys and API calls. Important key ranges and keys include `serverTagKeys`, `serverListKeys`, `keyServersPrefix`, `dataMoveKeys`, `datacenterReplicasKeys`, `dataDistributionModeKey`, `bulkLoadModeKey`, `bulkDumpModeKey`, `healthyZoneKey`, `rebalanceDDIgnoreKey`, `triggerDDTeamInfoPrintKey`, `moveKeysLockOwnerKey`, and `rebootWhenDurableKey`.

`updateReplicaKeys()` clears replica records for irrelevant DCs and caps primary/remote replica counts at the configured storage team size. `tryUpdateReplicasKeyForDc()` returns the old replica count and writes the new count; increases also set `rebootWhenDurableKey`, making replica-count growth durable through a reboot path.

`rewriteShardEncodedMetadata()` is an init-time rollback mechanism. It first clears all persisted `dataMoveKeys` in one transaction if any exist. After that, it scans up to 1000 `keyServers` rows per call and rewrites only rows encoded with shard location metadata back to old tag-based values. It returns `true` after committing so the caller restarts initialization and rereads a consistent view.

`getInitialDataDistribution()` builds substantial in-memory state in `InitialDataDistribution`: server list, TSS list, mode flags, bulk load/dump modes, healthy zone, all shards, primary and remote teams, recovered data moves, and tombstone data moves to clean. It deliberately avoids retrying after partially mutating result state inside a transaction attempt, using `succeeded` assertions to catch unsafe retry patterns.

The mock processor persists nothing to the database. It mutates `MockGlobalState`, including `allServers`, each mock server's `serverKeys`, and `shardMapping`. Mock APIs are intentionally immediate where possible to mimic transaction atomicity, while fetch completion is represented by mock shard status transitions.

## Dependencies and Integration Points

This file depends on the data-distribution interface in `fdbserver/datadistributor/DDTxnProcessor.h`, system-key and movement helpers from `MoveKeys`, data-distribution structures from `DataDistribution.h`, NativeAPI transaction helpers, management/configuration APIs, `DatabaseContext` storage and health metric calls, Flow coroutines/futures, transaction counters, tracing, knobs, `MockGlobalState`, and `ShardsAffectedByTeamFailure`.

The main runtime integration is `DataDistribution.cpp`, which constructs `DDTxnProcessor`, takes the move-keys lock, updates replica keys, calls `getInitialDataDistribution()`, and emits related `DDInit*` trace events. `DDRelocationQueue.actor.cpp` uses `getSourceServersForRange()` when choosing relocation sources. `DDShardTracker.cpp`, `DDTeamCollection.actor.cpp`, `TCInfo.cpp`, perpetual wiggle workloads, bulk load/dump workloads, and validation workloads use the interface for metrics, movement, or DD state.

The mock integration is centered on `IDDTxnProcessorApiCorrectness.cpp`, which exposes protected raw movement methods, reads real initial data, seeds `MockGlobalState`, runs real and mock start/finish or full `moveKeys()` operations, and verifies that shard boundaries and team mappings stay equivalent.

## Risks and Edge Cases

- `getSourceServersForRange()` falls back to all storage servers when too many key-server rows cover a range. That is conservative and crash-safe, but it can enlarge source sets and affect relocation scheduling behavior for fragmented or recovering ranges.
- `completeSources` depends on intersecting ordered source vectors across shards. Changes to source decoding or shard ordering can change relocation semantics.
- `getInitialDataDistribution()` mutates `InitialDataDistribution` while reading from retryable transactions. The `succeeded` assertions protect against duplicate accumulation after partial progress; any refactor must preserve that no-retry-after-mutation boundary.
- Shard-encoded metadata rollback intentionally clears all persisted data moves before rewriting key-server rows. This is safe only under the documented downgrade assumptions and because the caller restarts initialization after each commit.
- The rollback rewrite scans only the head 1000 key-server entries per call and loops by re-entering initialization. Bugs in the "did this row use shard encoding" test could cause repeated init churn or leave mixed encodings.
- `getHealthyZone()` may ignore maintenance mode after bounded read failures. This favors startup availability but can allow DD to move data for servers in maintenance zones until a restart or maintenance setting change succeeds.
- `tryUpdateReplicasKeyForDc()` sets `rebootWhenDurableKey` only on increases. Replica-key changes affect recovery and durability semantics, so changes here need careful multi-region testing.
- Mock raw movement currently asserts single-range movement when shard-encoded location metadata is enabled and has TODOs for multi-range support. It also assumes one destination team and one source team at finish, which may not cover future multi-region or dynamic-replica behavior.
- Mock `getWorkers()` and `getHealthMetrics()` are incomplete futures, and some mock interface methods are `UNREACHABLE()`. New consumers of `IDDTxnProcessor` need either mock support or explicit test exclusions.
- `rawStartMovement()` in the mock contains a direct `fmt::print`, so high-volume simulation may produce stdout noise independent of trace logging.

## Test Signals

The direct simulator test signal is `tests/fast/IDDTxnProcessorMoveKeys.toml`, which runs the `IDDTxnProcessorApiCorrectness` workload in raw start/finish mode and full `moveKeys()` mode. That workload compares real `DDTxnProcessor` behavior with `DDMockTxnProcessor` after randomized shard moves, splits, and merges in simulation.

Relevant trace signals include `DDInitShardEncodeOff`, `DDInitCancellingShardEncodedMoves`, `DDInitRewritingShardEncodedMetadata`, `DDInitSlowDataMoveRead`, `DDInitServerListAndDataMoveReadComplete`, `DDInitKeyServerScanProgress`, `DDInitKeyServerScanComplete`, `GetSourceServerInterfacesMissing`, `GetSourceServerInterfacesError`, `WaitForDDEnabledSucceeded`, `IsDDEnabledSucceeded`, `IsDDEnabledFailed`, `WaitForAllDataRemoved`, `RelocateShard_MockStartMoveKeys`, `RelocateShard_MockFinishMoveKeys`, and `MockRawFinishMovementError`.

Good regression coverage for changes here should include DD init after persisted data moves, rollback with `SHARD_ENCODE_LOCATION_METADATA` disabled, fragmented key-server source lookup, remote DC classification, maintenance-mode read failure behavior, replica-key updates, move-keys lock conflict retries, source/destination TSS handling through real movement helpers, and mock/real API equivalence under `IDDTxnProcessorApiCorrectness`.
