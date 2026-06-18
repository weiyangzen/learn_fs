# Research: sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008482`: lines 1-6163, `Docs/researches/chunks/subset-b-008482_research.md`
- `subset-b-008483`: lines 6164-12189, `Docs/researches/chunks/subset-b-008483_research.md`
- `subset-b-008484`: lines 12190-12732, `Docs/researches/chunks/subset-b-008484_research.md`

## Chunk Research

### subset-b-008482: lines 1-6163

# sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp lines 1-6163

## Scope

This chunk covers the beginning of FoundationDB's storage server actor implementation through the first part of the update section. It includes includes and persistent key-prefix definitions, move-in and adding shard state types, the central `StorageServer` state object, validation helpers, the major read RPC handlers, checkpoint serving, shard-state serving, mapped-range helpers, audit/restore validation paths, bulk-dump serving, range streaming, `getKey`, queue metrics, eager-read setup, and the start of durable-version advancement. The chunk ends inside `changeDurableVersion()`, so mutation application, shard changes, update log consumption, disk restore, server startup, and interface registration are outside this report.

## Purpose

The code defines the in-memory and durable state model used by an FDB storage server and implements much of the read-side RPC surface. Its main responsibilities in this range are:

- Maintain MVCC state by combining durable `IKeyValueStore` contents with an in-memory `VersionedMap<KeyRef, ValueOrClearToRef>` and a per-version mutation log.
- Track shard ownership and lifecycle through `ShardInfo`, including not-assigned, adding/fetching, moving-in physical shards, read-write pending, and readable states.
- Expose read APIs (`getValue`, `getKeyValues`, mapped range, streaming range, `getKey`) that wait for a readable version, verify shard ownership, merge storage-engine data with MVCC mutations, and return load-balancing penalties.
- Serve checkpoint discovery and checkpoint transfer for physical backup/data movement workflows.
- Support watches, range caching metadata, byte-sampling metadata, hot-range metrics, storage metrics, latency sampling, and read throttling based on durability lag.
- Run storage consistency/audit workflows comparing local shard metadata to system keyspaces, comparing restored backup data to source data, and comparing replicas for HA/replica validation.
- Serve bulk dump requests by reading local data, generating SST/manifest/sample files, uploading them, and persisting range-completion metadata.
- Prepare eager reads for mutation application by prefetching keys/values needed by atomic operations and selected clears.

## Important APIs, Types, and Functions

- Persistent key constants:
  - `persistFormat`, `persistShardAwareFormat`, `persistID`, `persistVersion`, `persistLogProtocol`, and `persistPrimaryLocality` encode storage-server identity/version/protocol metadata.
  - `persistShardAssignedKeys`, `persistShardAvailableKeys`, `persistStorageServerShardKeys`, `persistBulkLoadTaskKeys`, checkpoint prefixes, byte-sample prefixes, and accumulative-checksum prefixes describe durable metadata namespaces stored under `\xff\xff`.
  - `encodePersistAccumulativeChecksumKey()` and `decodePersistAccumulativeChecksumKey()` serialize checksum indexes with `bigEndian16`.

- Request/error helpers:
  - `canReplyWith()` lists errors that read/audit RPCs should return to callers instead of surfacing as actor failures, including `transaction_too_old`, `future_version`, `wrong_shard_server`, overload, mapper errors, and mapped-range quick-read misses.
  - `trackedReadType()` extracts `ReadOptions::type` when per-read-type latency tracking is enabled.
  - `dataMoveConflictError()` maps TSS data-movement conflicts to `please_reboot()` in simulation to avoid severity-40 test failures.

- Shard movement state:
  - `MoveInUpdates` buffers updates for physical shard move-in while the shard is not yet read-write. It can spill updates to the key-value store, load them back with `loadUpdates()`, and expose readiness through `hasNext()`.
  - `MoveInShard` wraps `MoveInShardMetaData`, fetch/apply promises, transfer version, phase, bulk-load mode, and mutation routing for physical shard move-in.
  - `AddingShard` models logical shard fetch during data movement, with phases `WaitPrevious`, `Fetching`, `FetchingCF`, and `Waiting`, plus deferred update buffering until fetch completes.
  - `ShardInfo` is the range-map value for ownership state. It converts to/from `StorageServerShard`, merges adjacent compatible shard entries, reports read/fetch readiness, routes mutations to adding/move-in/read-write paths, and stores physical shard IDs/version/team ID.

- Persistence adapter:
  - `StorageServerDisk` wraps `IKeyValueStore` with storage-server-specific counters and persistence helpers. In this chunk its interface includes durable-state creation/restoration, version/mutation durability, TSS quarantine persistence, log-protocol updates, range add/remove/replace for shard-aware stores, checkpoint/restore/delete, and counted read APIs.

- Main state object:
  - `StorageServer` owns `VersionedData versionedData`, `mutationLog`, watch metadata, `checkpoints`, `pendingCheckpoints`, physical-shard pending add/remove maps, histograms, `shards`, `newestAvailableVersion`, `newestDirtyVersion`, version notifiers, log-system cursor state, TSS pairing/quarantine state, locks, rate limiters, audit/dump locks, counters, metrics, and database handles.
  - `StorageServer::Counters` extends `CommonStorageCounters` with query counts, get-mapped-range stats, logical input/durable bytes, storage-engine read/commit counters, fetch metrics, PTree metrics, shard-change counters, read latency samples, latency bands, and special live counters for versions, locks, watches, rates, and kvstore sizes.
  - `currentRate()`, `getPenalty()`, `shouldRead()`, `readGuard()`, and `getQueryDelay()` implement local read admission and load-balancing penalty behavior based on durability lag and queue size.
  - `addVersionToMutationLog()`, `addMutationToMutationLog()`, and `addMutationToMutationLogOrStorage()` bridge MVCC/mutation-log accounting and byte sampling.

- Read/version helpers:
  - `waitForVersionActor()`, `waitForVersion()`, and `waitForVersionNoTooOld()` wait for the storage server to reach a requested version, handle `latestVersion`, version-vector commit-version optimization, `transaction_too_old`, `future_version`, and `process_behind`.
  - `getRealReadVersion()` and `getLatestCommitVersion()` use `VersionVector` and the storage server's tag to choose a safe read version when version vectors indicate no mutations happened between commit and requested read versions.
  - `getShardKeyRange()` finds the contiguous readable shard span around a key selector and throws `wrong_shard_server()` when the selector is outside readable ownership.

- Point/range reads:
  - `getValueQ()` serves `GetValueRequest` using MVCC first and durable storage second, validates shard changes after storage IO, updates read metrics, and returns `GetValueReply` with cache flag and penalty.
  - `merge()` combines durable `RangeResult` data with newer `VersionedMap` sets, respecting forward/reverse limits and byte limits.
  - `readRange()` reads a key range at a version by alternating MVCC traversal and storage reads, skipping clears, merging results, and computing `more`, byte, row, and logical-size metrics.
  - `findKey()` implements key-selector resolution within one readable shard, returning either an exact key or an offset/key pair that tells the caller the selector escaped the shard or byte limit.
  - `getKeyValuesQ()`, `getKeyValuesStreamQ()`, and `getKeyQ()` layer shard validation, key-selector handling, range reads, streaming continuations, transaction-tag accounting, and latency metrics over these helpers.

- Watches:
  - `ServerWatchMetadata` tracks the key, expected value, original version, tags, debug ID, and shared watch actor state for storage-server watches.
  - `watchWaitForValueChange()` repeatedly reads the watched key at safe versions, subscribes to `AsyncMap` changes, handles races with newer watch versions, and limits watch memory.
  - `watchValueSendReply()` wraps the watch future with timeout handling, fast timeout when no recent updates exist, watch-byte accounting, cancellation cleanup, and reply/error delivery.

- Checkpoint serving:
  - `getCheckpointQ()` waits for the requested version to be durable, verifies the requested range is readable, and returns a completed checkpoint matching version/format/action/range.
  - `deleteCheckpointQ()` waits for durability, removes checkpoint files, erases in-memory state, and writes mutation-log clears for both pending and completed checkpoint metadata keys.
  - `fetchCheckpointQ()` streams raw checkpoint chunks from `ICheckpointReader`.
  - `fetchCheckpointKeyValuesQ()` streams checkpoint contents as key-value batches, with per-server parallelism limiting and reuse/cleanup of `liveCheckpointReaders`.

- Mapped range helpers:
  - `quickGetValue()` and `quickGetKeyValues()` attempt local storage-server reads for secondary mapped lookups and optionally fall back to normal database transactions.
  - `preprocessMappedKey()`, `constructMappedKey()`, tuple unpack helpers, and literal escaping parse mapper tuple templates containing literals, `{K[n]}`, `{V[n]}`, and `{...}` range-query markers.
  - `mapSubquery()`, `mapKeyValues()`, and `getMappedKeyValuesQ()` scan index rows, construct mapped keys, dispatch point/range subqueries in bounded parallel batches, enforce byte limits, and preserve first/last index entries for continuation.

- Audit and validation:
  - `getThisServerShardInfo()` extracts local shard ownership over an audit range from `StorageServer::shards`.
  - `auditStorageServerShardQ()` compares local shard info with `serverKeys` and `keyServers` system keyspace views, records shard-assignment history during version catch-up, persists per-server audit state, and rate-limits remote reads.
  - `fetchSourceAndRestoredData()`, `compareSourceAndRestoredData()`, and `auditRestoreQ()` validate backup restore output by comparing normal-key source data with restore-prefixed data under `validateRestoreLogKeys`.
  - `issueGetKeyValuesRequest()` and `auditStorageShardReplicaQ()` compare local and remote storage-server range reads for HA/replica validation, persisting range progress and error state.

- Bulk dump:
  - `getRangeDataToDump()` reads local range data in batches using `getKeyValuesQ()`, builds raw KV and byte-sample maps, and returns `retry()` when the first read fails.
  - `bulkDumpQ()` serializes a requested range to local SST/manifest/sample files, uploads the resulting file set, persists completed bulk-dump range metadata, batches by size/count knobs, handles retryable failures, and best-effort cleans local task folders.

- Metrics and update prelude:
  - `getQueuingMetrics()` returns queue/durability/storage/rate/cpu/disk/busiest-tag status to the caller.
  - `doEagerReads()` deduplicates eager-read keys, reads key ends for clear-range conversion and value prefixes for atomics, stores results in `UpdateEagerReadInfo`, and records storage-engine read metrics.
  - `changeDurableVersion()` begins the process of pruning already-durable MVCC entries and mutation-log/freeable state; the function continues beyond this chunk.

## Control Flow

Storage-server read RPCs follow a repeated pattern. They increment counters and queue-size tracking, optionally yield at a priority that prevents load-balancing probes from dominating endpoint work, acquire a read priority lock, wait for a version using either the request version or version-vector commit version, capture the current `shardChangeCounter`, verify shard readability, perform MVCC/storage reads, then re-check `shardChangeCounter` before replying. Errors in the `canReplyWith()` list are converted into replies with current penalty where applicable; other errors abort the actor.

`getValueQ()` performs a point lookup by first checking `versionedData.at(version).lastLessOrEqual(key)`. If it finds a set for the exact key, it returns that value. If no relevant clear covers the key, it reads the durable store. After any storage read it rejects the result if the requested version fell behind `storageVersion()` or if shard metadata changed concurrently. The result updates empty/nonempty row counters, byte counters, read sampling, cache metadata, transaction tag counters, latency samples, and latency-band measurements.

Range reads are split across `getKeyValuesQ()`, `findKey()`, and `readRange()`. `getKeyValuesQ()` resolves selectors inside the contiguous readable shard span, treats offsets other than 0/1 as `wrong_shard_server`, and handles empty ranges directly. `readRange()` then walks the versioned PTree and the durable storage engine in ascending or descending direction. It detects clear ranges in MVCC, bounds storage reads to the next MVCC key or clear end, merges durable and MVCC rows, decrements row and byte limits, and reports whether there may be more rows. This is the core control path used by normal range reads, key-selector resolution, audit local reads, bulk dump reads, and stream batches.

`getKeyValuesStreamQ()` uses the same selector validation but sends multiple `GetKeyValuesStreamReply` messages. Each iteration waits for the reply stream to be ready, acquires a read lock, verifies the fixed version is still not too old, reads a batch, sends it, advances `begin` or `end` by the last key depending on direction, and finally sends `end_of_stream()`. Unlike non-stream range reads, this actor holds version constant across chunks and must reject with `transaction_too_old` if the storage server advances oldest version too far.

Mapped-range control flow starts like a normal range read to fetch index rows. It then releases the read lock before issuing mapped subqueries, because those subqueries re-enter `getValueQ()` or `getKeyValuesQ()` and would otherwise contend with the same read lock held by the parent. Mapper parsing turns a tuple template into either a point-mapped key or a prefix range query. Subqueries run in batches capped by `MAX_PARALLEL_QUICK_GET_VALUE`; local misses optionally fall back to database transactions. The response keeps boundary index entries so callers can continue from the right position.

Watch control flow shares one `ServerWatchMetadata` per watched key. The watch actor waits until the desired version is known, repeatedly reads the key at current server version, fires when the value differs at or after the requested version, otherwise subscribes to `watches.onChange(key)` or waits for a newer version needed to resolve races. `watchValueSendReply()` runs the caller-facing timeout loop, adjusting timeout mode when `noRecentUpdates` changes and cleaning the shared watch actor when the last promise reference disappears.

Checkpoint serving first ensures the checkpoint version is durable. Discovery (`getCheckpointQ`) scans the in-memory checkpoint map for completed metadata matching version/action/range. Raw transfer (`fetchCheckpointQ`) sends chunks until `end_of_stream` or `checkpoint_not_found`. Key-value transfer (`fetchCheckpointKeyValuesQ`) guards parallelism, lazily creates/reuses a key-value checkpoint reader, streams iterator batches, and closes/removes readers when no longer in use.

Audit actors are long-running, lock-limited flows. `auditStorageServerShardQ()` reads local shard info at the storage server's current version, enables shard-assignment history tracking, reads `serverKeys` and `keyServers` transactionally until their read version is at least the local view version, waits for the storage server to catch up, rejects if any shard assignment happened in the interval, then compares the three ownership views over an overlapping claim range. It persists complete or error state and advances through partial KRM reads under a rate limiter.

`auditRestoreQ()` validates source normal-key data against restore-prefixed data. It uses database transactions for both sides to avoid local shard-boundary artifacts, compares keys after stripping the restore prefix, fails fast if either side is completely empty at the start while the other is non-empty, periodically persists running progress by byte interval, and persists final complete/error state. `auditStorageShardReplicaQ()` gathers remote `StorageServerInterface`s from `serverList`, chooses a transaction read version, requests range data from each remote plus local, compares key/value sequences pairwise, persists progress every 100 checks or at completion, and reports the first mismatch as audit error.

`bulkDumpQ()` is an SS-side data-export loop. For each batch it clears local task files, gets a read version, calls `getRangeDataToDump()`, computes local and remote file-set paths, constructs byte-sampling settings, writes local SST/manifest/sample files, uploads only files that exist, persists completed range metadata, then advances to `keyAfter(lastKey)`. It retries most errors up to a high count, but gives up on task-outdated, shard-server, platform, and IO errors, and always attempts local cleanup at the end.

## State and Persistence Behavior

The chunk's central state split is durable storage versus MVCC overlay. Durable user data and storage-server metadata live in `IKeyValueStore`. Recent mutations live in `versionedData` and `mutationLog` until made durable. `oldestVersion`/`durableVersion`/`desiredOldestVersion` define the readable MVCC window and the point to which recovery can rely on disk. The comments on `StorageServer::versionedData` define invariants: clears are non-overlapping and maximal, reads combine storage plus `VersionedMap`, versioned data spans `[storageVersion(), version]`, old shard entries are eventually erased, and latest entries must have insert versions newer than `durableVersion`.

Shard state is persisted and exposed through both logical assignment ranges and physical shard-aware metadata. `StorageServer::shards` stores live `ShardInfo` entries. `newestAvailableVersion` and `newestDirtyVersion` track readability and partial availability. `persistShardAssignedKeys`, `persistShardAvailableKeys`, `persistStorageServerShardKeys`, pending checkpoint keys, pending physical-shard add/remove maps, and bulk-load task metadata are the durable side of this state. In shard-aware stores, `StorageServerDisk` also delegates physical range mapping to `IKeyValueStore::addRange`, `removeRange`, `replaceRange`, and `persistRangeMapping`.

Move-in state can be memory-only or spilled. `MoveInUpdates::loadUpdates()` reads serialized `VerUpdateRef` values from keys derived from move-in ID and version, restores older updates ahead of in-memory updates, uses a spill buffer when a range read returns `more`, and clears the spilled flag only when the last batch is loaded. `AddingShard` and `MoveInShard` both gate read/write availability through promises and phase changes; their deferred updates must be replayed only after fetched data is ready.

Checkpoint state is both in-memory and durable/file-backed. `StorageServer::pendingCheckpoints` and `checkpoints` track pending and completed metadata. Completed checkpoint files are read by `ICheckpointReader`, and deletion clears both checkpoint files and persisted metadata keys by adding clear mutations to the current mutation log. `liveCheckpointReaders` retains active readers for key-value checkpoint streaming until no iterator is using them.

Audit and restore validation persist state back through the normal database API rather than local storage-engine metadata. `persistAuditStateByServer()` and `persistAuditStateByRange()` record progress/error/complete state tied to audit IDs, DD IDs, ranges, and server IDs. The actors use transactional reads of system keyspaces (`serverKeys`, `keyServers`, `serverList`) and lock-aware/system-key options, so their correctness depends on consistent cluster metadata versions as well as local shard metadata.

Bulk dump persistence spans local disk, remote blob/storage transport, and system metadata. The actor first writes local SST and manifest artifacts under the storage server's bulk dump folder, uploads to the job/task/batch remote path, and then persists the completed range's manifest metadata. Cleanup deletes local task files best-effort; remote inconsistency is expected to be detected by the DD and retried with a new task.

TSS state affects read behavior. A server with `tssPairID` is a TSS; `tssInQuarantine` can be persisted via `makeTssQuarantineDurable()`. Quarantined TSSs reject reads via `shouldRead()` but remain alive enough for operator investigation and eventual removal.

## Dependencies and Integration Points

- Flow actor runtime: functions return `Future<T>`, use `co_await`, `ACTOR`, `choose`, `Promise`, `FutureStream`, `AsyncVar`, `AsyncMap`, `FlowLock`, `PriorityMultiLock`, `ThroughputLimiter`, `SpeedLimit`, and actor collection management.
- FDB client/server interfaces: request/reply types such as `GetValueRequest`, `GetKeyValuesRequest`, `GetMappedKeyValuesRequest`, `GetKeyValuesStreamRequest`, `GetKeyRequest`, `WatchValueRequest`, `GetCheckpointRequest`, `FetchCheckpointRequest`, `AuditStorageRequest`, `BulkDumpRequest`, and `StorageQueuingMetricsRequest` define the external RPC surface.
- Storage engine abstraction: `IKeyValueStore` supplies durable reads/writes, range management, checkpoints, restore, physical shard operations, and storage-byte accounting. This code assumes its range reads obey row/byte limits and `more` semantics.
- Log system and data movement: included dependencies and state refer to `LogSystemConsumer`, `IReplayPeekCursor`, `TLogInterface`, `MoveKeys`, `DataMovement`, `StorageServerShard`, and physical shard move metadata. Later chunks implement update consumption and shard changes, but this chunk defines much of the state they mutate.
- System keyspace/database transactions: audit, restore validation, mapped-range fallback, and bulk-dump metadata persistence use `Database`, `Transaction`, system-key options, lock-aware options, `serverListKeyFor()`, `getThisServerKeysFromServerKeys()`, `getShardMapFromKeyServers()`, and audit/bulk-load persistence helpers.
- Tuple and mapper contracts: mapped-range APIs depend on `Tuple::unpack`, tuple element raw strings, and user-facing mapper template syntax. Errors are mapped to specific mapper error codes.
- Metrics/tracing: `TraceEvent`, `g_traceBatch`, `ReadLatencySamples`, `LatencyBands`, histograms, `CommonStorageCounters`, `StorageMetrics`, hot-range metrics, transaction tag counters, and event cache holders are deeply integrated with every read/audit/data-transfer path.
- Simulation and test hooks: `buggify()`, `CODE_PROBE`, `g_network->isSimulated()`, `FDBSimulationPolicy`, consistency-scan corruption injection, targeted restart/delay injection, and TSS fault injection shape edge-case behavior in tests.
- Bulk load/dump/checkpoint utility layers: `BulkDumpUtil`, `BulkLoadUtil`, `ServerCheckpoint`, checkpoint readers/iterators, byte-sample helpers, file upload helpers, and local folder cleanup are used by checkpoint and dump handlers.

## Risks and Edge Cases

- MVCC/storage merge correctness is delicate. `readRange()` must correctly account for clears spanning the requested bounds, forward versus reverse ordering, storage `more` semantics, byte limits, and duplicate keys where MVCC sets override durable values.
- Shard-change races are explicitly guarded by `shardChangeCounter`. Missing a post-IO check would let a read answer for a range that moved away while the storage read was in progress.
- Version-window errors are split across `transaction_too_old`, `future_version`, and `process_behind`. Version-vector optimization can legally read at a commit version older than the requested read version only when the tag has no newer mutations; mistakes here would violate snapshot semantics.
- Read throttling depends on durability lag and random rejection. `shouldRead()` must reject quarantined TSS reads and overload only replyable request types; otherwise clients may see actor failures instead of load-balanced retries.
- Mapped-range subqueries are reentrant. The parent releases the read lock before launching subqueries; holding it would create self-contention or deadlock under the same priority lock. Conversely, releasing it means shard state must be revalidated after mapping.
- Mapper parsing trusts tuple structure but must reject bad indexes, malformed tuple keys/values, non-final `{...}`, and non-tuple mapper inputs with the correct public errors.
- Watches can consume unbounded memory if not capped. The code tracks both queued watch overhead and implementation overhead; exceeding `MAX_STORAGE_SERVER_WATCH_BYTES` cancels watches and falls back to polling behavior.
- Audit shard validation currently gives up if shard assignment history is non-empty between the local view and system-key read version rather than replaying history. This is conservative but can produce failed/cancelled audit work under active data movement.
- Audit flows rely on per-server parallelism lock being one for shard-info audits because `trackShardAssignmentMinVersion` is a single shared state. Increasing the lock without redesign would make concurrent audits interfere.
- Restore validation has asymmetric empty-side fast failures and compares prefixed restored keys after stripping `validateRestoreLogKeys.begin`. Wrong prefix/range construction would turn valid restore output into false missing/extra-key errors.
- Replica validation considers any completed read among replicas enough to mark the round complete; if other replies have `more`, size/key mismatches surface as errors in that round. This intentionally catches inconsistency but makes limit alignment important.
- Bulk dump writes/upload/persist is not atomic across local files, remote files, and database metadata. The comments rely on DD retry/verification to detect remote inconsistencies; local cleanup is best effort.
- Checkpoint streaming owns raw reader pointers in `liveCheckpointReaders`. Correct `inUse()` checks and close/erase ordering are required to avoid leaks or closing a reader still backing an iterator.
- `getKeyValuesStreamQ()` does not use the same initial read-admission path as normal range reads; it yields at endpoint priority and then repeatedly locks per batch. It must still guard too-old versions inside the loop.
- The chunk ends as durable-version pruning begins. Full risk analysis of mutation-log deletion, `freeable` arenas, and VersionedMap forgetting requires the continuation after line 6163.

## Test Signals

- Point reads: values present in MVCC, values present only on disk, keys covered by MVCC clears, absent keys, cached-range flags, system-key counters, debug IDs, overloaded/quarantined TSS rejection, and post-read shard-change `wrong_shard_server`.
- Version handling: `latestVersion`, too-old reads, future-version timeout, process-behind behavior, version-vector commit-version reads, and reads around `oldestVersion` advancement during storage IO.
- Range reads: forward/reverse scans, clear ranges crossing begin/end, MVCC overriding durable rows, byte-limit and row-limit `more`, large selector offsets returning `wrong_shard_server`, empty ranges, contiguous readable shard boundaries, consistency-scan corruption injection in simulation, and range-stream continuations to `end_of_stream`.
- Key selectors: exact keys, `firstGreaterOrEqual`, backward selectors at shard boundaries, selectors escaping shard boundaries with offset 1, large offsets that hit byte limits, and reverse selector one-row edge cases.
- Watches: immediate value change, timeout with and without `noRecentUpdates`, racing watches for the same key/version, transaction-too-old retry in the watch loop, watch memory cap cancellation, and cleanup when the last promise reference disappears.
- Checkpoints: checkpoint lookup by version/format/action/range, unreadable range rejection, checkpoint-not-found, raw chunk streaming, key-value checkpoint streaming, active reader reuse, iterator end-of-stream, and checkpoint deletion clearing both file and metadata keys.
- Mapped ranges: mapper literal escaping, `{K[n]}` and `{V[n]}` extraction, `{...}` prefix range queries, non-tuple key/value/mapper errors, bad indexes, local quick-get hit/miss counters, fallback enabled/disabled, byte-limit truncation, and preserved boundary index rows for continuation.
- Audit shard validation: mismatch between `serverKeys`, `keyServers`, and local `shards`; partial KRM reads; system-key read version behind local version requiring retry; shard-assignment history non-empty during audit; DD ID validation; progress/error persistence; and rate limiter accounting.
- Restore validation: matching source/restored ranges, missing key, extra key, value mismatch, empty baseline/source fast paths, retryable future/too-old/overload errors, periodic running-progress persistence, and final error/complete state.
- Replica audit: missing remote server list entries, remote RPC errors, local/remote key mismatch, value mismatch, missing local or remote keys, nothing-to-compare case, partial progress persistence every 100 checks, and wrong-shard handling for out-of-range returned keys.
- Bulk dump: empty range manifest, batches split by byte and count limits, byte sample file generation/omission, local folder cleanup, upload failure retry, task-outdated handling, wrong-shard/platform/IO failure mapping, and persisted completed range metadata matching manifest range.
- Metrics and throttling: queue metric replies, busiest tag reporting, latency-band filtering for large reads or selector offsets, read-priority mapping by `ReadType`, local rate changes as durability lag crosses soft/hard thresholds, and storage-engine read counters from eager reads.

### subset-b-008483: lines 6164-12189

# sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp lines 6164-12189

## Scope

This chunk covers the central storage-server mutation and durability path after mutation-log cleanup, plus shard movement, fetchKeys, physical shard move/checkpoint ingestion, durable-state restore, byte-sample maintenance, storage request service loops, and storage-server termination. It starts inside `changeDurableVersion()` cleanup and ends at the beginning of `memoryStoreRecover()`, so process startup above this range and the remaining recovery helpers below it are outside this chunk.

## Purpose

The code in this range turns TLog mutations and data-movement state transitions into in-memory MVCC state and durable `IKeyValueStore` contents. It owns the mechanics for applying normal mutations, converting atomic mutations, expanding clears, splitting mutations by shard, fetching data for newly assigned ranges, persisting shard availability/assignment metadata, restoring persistent storage-server state after restart, and serving the storage-server RPC surface once the core loop is running.

For sharded RocksDB / physical shard movement, this chunk also implements the move-in lifecycle: fetch checkpoint or bulk-load SST metadata, restore checkpoint files into the storage engine, apply logged updates accumulated during the fetch, transition shards to read-write, and clean up persisted move-in records. For non-shard-aware stores, the same shard assignment events still flow through `AddingShard` and logical `fetchKeys()`.

## Important APIs, Types, and Functions

- `changeDurableVersion()` tail logic forgets durable MVCC/mutation-log versions, updates `storageMinRecoverVersion`, advances `durableVersion`, updates global debug durable state with `setDataDurableVersion()`, and validates the storage server.
- `clipMutation()`, `convertAtomicOp()`, `expandClear()`, and free `applyMutation()` normalize mutations before they enter `VersionedData`: atomic ops become `SetValue` or `ClearRange`, clear ranges are expanded to preserve clear-to bookkeeping, and sets split existing clear intervals.
- `removeDataRange()` removes a key range from the latest MVCC version while adding mutation-log entries needed to make the removal durable and forgettable.
- `coalesceShards()`, `splitMutation()`, and `splitMutations()` map mutation ranges onto `KeyRangeMap` shard intervals, routing writes to `AddingShard`, `MoveInShard`, or read-write shard targets.
- `FetchKeysMetricReporter`, `tryGetRange()`, `tryGetRangeForBulkLoad()`, `tryGetRangeForBulkLoadFromSST()`, `bulkLoadFetchKeyValueFileToLoad()`, `processSampleFiles()`, and `fetchKeys()` implement logical range movement from storage-server reads or local SST bulk-load files.
- `AddingShard::addMutation()` buffers mutations while data is being fetched, discards versions already covered by `fetchVersion`, and forwards mutations to normal storage once the fetch reaches feed-catchup phases.
- `changeServerKeys()` is the logical shard-assignment state machine. It processes assigned/unassigned range changes, starts `AddingShard` fetches, removes data for unassigned ranges, assigns empty ranges, persists availability and bulk-load metadata, and updates `newestAvailableVersion` / `newestDirtyVersion`.
- `changeServerKeysWithPhysicalShards()` is the shard-aware equivalent. It handles `StorageServerShard` states (`NotAssigned`, `Adding`, `MovingIn`, `ReadWritePending`, `ReadWrite`), move-in conflicts, physical shard IDs derived from data-move IDs, fallback to logical adding, and persistent shard metadata.
- `fallBackToAddingShard()`, `bulkLoadFetchShardFileToLoad()`, `fetchShardCheckpoint()`, `fetchShardIngestCheckpoint()`, `fetchShardApplyUpdates()`, `cleanUpMoveInShard()`, and `fetchShard()` implement the `MoveInShard` lifecycle.
- `MoveInUpdates` tracks mutations for a physical shard move between checkpoint creation and read-write transition. It supports in-memory buffering, spill-state restoration from `persistUpdatesKeyRange()`, byte-limited `next()` batches, and failure cancellation.
- `MoveInShard` owns move-in metadata, affected ranges, fetch actor lifetime, phase transitions, high watermark, cancellation, and forwarding of mutations either into `MoveInUpdates` or normal storage.
- `ShardInfo::newShard()` and `ShardInfo::addMutation()` create and dispatch per-range shard state for assigned, adding, moving-in, read-write-pending, read-write, and not-assigned ranges.
- `restoreShards()` reconstructs shard-aware `ShardInfo`, `MoveInShard`, assignment, and availability maps from persisted storage metadata.
- `StorageUpdater` is the per-update batch applier. It creates new MVCC versions, applies private mutations, handles server-key range assignment pairs, reacts to rollback and kill/tag private keys, persists TSS pair/quarantine/primary-locality state, updates accumulative checksums, and registers checkpoint requests.
- `update()` is the TLog replay loop. It enforces storage e-brake backpressure, reads from the replay cursor, gathers eager reads, injects completed fetchKeys / physical-shard updates, applies mutations, and advances `version` / `desiredOldestVersion`.
- `createCheckpoint()` and `createSstFileForCheckpointShardBytesSample()` create storage checkpoints and byte-sample SST files, then persist checkpoint metadata or schedule cleanup on failure.
- `updateStorage()` is the durable commit loop. It chooses a target durable version, handles pending add/remove KVS ranges and checkpoint barriers, writes mutation-log entries through `StorageServerDisk`, commits the storage engine, advances durable version, prunes MVCC state, persists move-in update spill records, and resets fetchKeys commit budget.
- `StorageServerDisk` helpers persist initial format, shard metadata, assigned/available/bulk-load range maps, mutation batches, storage version, TSS quarantine, and protocol version.
- `restoreDurableState()` reads persisted IDs, versions, shard maps, checkpoints, move-in records, accumulative checksum state, bulk-load metadata, and byte samples to reconstruct an initialized `StorageServer`.
- `StorageServer::byteSampleApplySet()` and `byteSampleApplyClear()` keep the in-memory sampled byte map and the persisted `persistByteSampleKeys` range synchronized.
- `metricsCore()`, request-serving actors, `storageEngineConsistencyCheck()`, `reportStorageServerState()`, and `storageServerCore()` start the live service surface: reads, range reads, mapped reads, watches, metrics, checkpoints, audit, bulk dump, hot-shard reporting, and update dispatch.
- `storageServerTerminated()` shuts down fetch actors by replacing all shards with not-assigned, then closes or disposes the `IKeyValueStore` depending on whether the server is rebooting, removed, failed recruitment, or simply cancelled.

## Control Flow

Normal mutation flow begins in `update()`. The storage server waits for TLog cursor data, takes `durableVersionLock`, scans a cloned cursor to collect eager-read requirements, injects any ready fetchKeys or physical-shard update batches, performs eager reads, then applies injected and TLog mutations through `StorageUpdater`. Public key mutations are split through `splitMutation()` to the current shard target. Private mutations drive range assignment, rollback, worker removal, pair/quarantine metadata, checkpoints, and checksum persistence.

`StorageServer::addMutation()` is the final mutation normalization path for user data. It ensures a mutation-log version exists, converts atomic ops by reading latest MVCC or eager-read state, expands clears to cover existing clear markers or trusted eager-read boundaries, appends the normalized mutation to the mutation log, and applies it to `VersionedData`. Sets may split a clear interval and trigger point watches. Clears erase the interval, insert a clear-to marker, trigger range watches, and update counters.

Logical data movement is initiated by private server-key mutations decoded in `StorageUpdater::applyPrivateData()`. `changeServerKeys()` first short-circuits no-op assignment changes, saves old shard references so cancellation side effects happen after shard-map realignment, reinitializes affected ranges, and then handles each intersecting range. Assigning unavailable ranges creates `AddingShard` state unless this is initial cluster seeding or assign-empty recovery. Unassigning readable ranges records the version at which they became unavailable, removes their data through `removeDataRange()`, persists availability false, and triggers watches. Once a fetch completes, `fetchKeys()` injects accumulated mutations into a future update batch, persists availability true, waits for durability, updates `newestAvailableVersion`, and replaces the shard with read-write state.

`fetchKeys()` is deliberately staged. It waits for the core loop and, if needed, version advancement after restore; waits until prior availability/dirty versions for the range are durable; takes `fetchKeysParallelismLock`; chooses a fetch version, optionally using GRV after transaction-too-old errors; streams blocks from the database or from local bulk-load SST files; writes each block directly with `storage.replaceRange()`; updates byte samples; throttles through fetch budget and limiter state; and retries known transient errors. Partial progress can split the adding shard into fetched and not-yet-fetched halves. After direct writes are durable, it waits for TLog feed catch-up, injects buffered updates into `FetchInjectionInfo`, writes final availability metadata, and transitions the shard to read-write.

Bulk load has two logical paths in this chunk. For normal `fetchKeys()`, metadata is read from data-move state, files are downloaded, and the server either ingests SST files directly when the storage engine supports it and ranges align, or falls back to KV-block replacement via `tryGetRangeForBulkLoad()`. For physical shard movement, `bulkLoadFetchShardFileToLoad()` downloads a single manifest file set, regenerates byte samples if settings differ, wraps the local SST as `CheckpointMetaData`, and moves the `MoveInShard` to `Ingesting`.

Physical shard movement goes through `changeServerKeysWithPhysicalShards()` and `fetchShard()`. Assignment creates or updates a `MoveInShard` keyed by data-move ID, persists `StorageServerShard::MovingIn`, and marks the range dirty. `fetchShard()` waits for core startup, durability of the create version, and the fetch parallelism lock, then loops over phase-specific handlers. `Fetching` obtains checkpoints or bulk-load files. `Ingesting` restores checkpoints into the storage engine and persists range mappings. `ApplyingUpdates` repeatedly injects `MoveInUpdates` into normal update batches until the high watermark catches up, then marks shard metadata complete/read-write-pending and waits for durability. The final transition replaces each range with read-write `ShardInfo`, sets availability, signals `readWrite`, validates, and schedules cleanup.

Durability is handled independently by `updateStorage()`. It waits for `desiredOldestVersion` or fetch budget pressure, sets `durableInProgress`, applies storage-engine range add/remove barriers and checkpoint barriers, calls `makeVersionMutationsDurable()` until the selected version or byte/clear limits are reached, forgets old MVCC versions, optionally lends remaining commit budget to fetchKeys, persists move-in update spill records, writes the durable version marker, commits, removes obsolete KVS ranges after commit, creates checkpoints exactly at required durable versions, handles reboot-when-durable, and finally advances `durableVersion` with `changeDurableVersion()` under the durable-version lock.

Recovery starts in `restoreDurableState()`. It reads point metadata and range metadata in parallel, starts byte-sample recovery, validates format, restores IDs and pair/quarantine state, sets the server-key prefix, restores log protocol and primary locality, restores pending and completed checkpoints, reconstructs `newestAvailableVersion`, restores accumulative checksum state, reconstructs bulk-load range metadata, then either delegates shard-aware reconstruction to `restoreShards()` or replays legacy assigned-range metadata through `changeServerKeys(..., CSK_RESTORE, ...)`. Non-shard-aware recovery clears storage data for unavailable ranges after reconstruction.

`storageServerCore()` wires everything together after durable state exists. It starts `updateStorage()`, failure handling, metrics, read-serving actors, watch-serving actors, diagnostic/reporting actors, and the storage-engine consistency checker, then enters a `choose` loop for database-info changes, shard-state requests, queue metrics, storage type, update completion/restart, checkpoint/fetch-checkpoint, commit-cost updates, audit, bulk dump, hot-shard requests, and actor failures.

## State and Persistence Behavior

- MVCC state lives in `VersionedData`, `mutationLog`, `freeable`, `oldestVersion`, `version`, `desiredOldestVersion`, `durableVersion`, and `storageMinRecoverVersion`. `changeDurableVersion()` and `updateStorage()` jointly determine when in-memory history and mutation-log entries can be forgotten.
- Shard state is kept in `data->shards`, `newestAvailableVersion`, `newestDirtyVersion`, `pendingAddRanges`, `pendingRemoveRanges`, `pendingAddRanges`, `ssBulkLoadMetadataMap`, `moveInShards`, and per-shard `AddingShard` / `MoveInShard` actors.
- Legacy assignment/availability persistence uses `persistShardAssignedKeys` and `persistShardAvailableKeys` as range maps. Bulk-load intent uses `persistBulkLoadTaskKeys`. Shard-aware persistence uses `persistStorageServerShardKeys` plus `persistMoveInShardKey()` records.
- Physical shard move update spill data is stored under `persistUpdatesKeyRange(moveInShardId)`. `MoveInUpdates` can resume from spilled state and `cleanUpMoveInShard()` clears spill ranges after completion or cancellation when safe.
- Storage format and identity are persisted through `persistFormat` or `persistShardAwareFormat`, `persistID`, `persistVersion`, `persistTssPairID`, `persistSSPairID`, `persistTssQuarantine`, `persistLogProtocol`, and `persistPrimaryLocality`.
- Checkpoint state is persisted through `persistPendingCheckpointKeys` and `persistCheckpointKeys`. Pending checkpoint requests block `updateStorage()` at the target version so checkpoint files represent the requested durable state.
- Byte-sampling state is maintained both in memory (`metrics.byteSample.sample`, `byteSampleClears`, `byteSampleRecovery`) and on disk under `persistByteSampleKeys`. Recovery first reads byte-sample sample ranges, then restores sample data in parallel chunks after core durable state is ready.
- Accumulative checksum validator state is restored from and persisted to `persistAccumulativeChecksumKeys`.
- Direct `storage.replaceRange()`, `storage.addRange()`, `storage.removeRange()`, `storage.persistRangeMapping()`, checkpoint `restore()`, and SST ingestion calls mutate the storage engine outside normal mutation-log writes, but the code pairs them with durable-version waits and metadata mutations so recovery can reconcile state.

## Dependencies and Integration Points

- Flow actors and concurrency primitives: `Future`, `Promise`, `PromiseStream`, `FutureStream`, `choose`, `wait`, `waitNext`, `getAll`, `waitForAll`, `delay`, `FlowLock`, `AsyncVar`, actor cancellation, and task priorities are used throughout.
- FoundationDB transaction/client API: `Transaction`, `getRange`, `getRangeStream`, `getRawReadVersion`, transaction options, read options, database cache invalidation, and system-key metadata readers are used by fetchKeys, bulk load, and checkpoint fetch paths.
- Storage abstractions: `IKeyValueStore`, `StorageServerDisk`, `StorageServerShard`, `CheckpointMetaData`, `RocksDBCheckpointKeyValues`, SST ingestion, range mapping, byte-sample readers, and storage-engine consistency APIs connect storage-server logic to memory/RocksDB/sharded RocksDB engines.
- Data distribution and shard movement: server-key private mutations, `decodeServerKeysValue()`, `DataMoveType`, `DataMovementReason`, `SSBulkLoadMetadata`, data-move IDs, `BulkLoadTaskState`, and data-move conflict errors link this code to DD decisions.
- Mutation and MVCC primitives: `MutationRef`, `VerUpdateRef`, `VersionedMap`, eager-read info, byte-sample helpers, mutation checksums, and accumulative checksum validation provide mutation correctness.
- System keys and persistence helpers: `persist*` key ranges, `serverKeysPrefixFor()`, `tssMappingKeys`, `tssQuarantineKeys`, `lastEpochEndPrivateKey`, `killStoragePrivateKey`, `rebootWhenDurablePrivateKey`, and checkpoint/bulk-load metadata codecs are central integration points.
- Observability and test hooks: `TraceEvent`, `TraceInterval`, `DEBUG_MUTATION`, `DEBUG_KEY_RANGE`, `CODE_PROBE`, histograms, counters, `EventCacheHolder`, `SimBugInjector`, buggify paths, and storage-corruption injection are woven into state transitions.
- Request handling: `StorageServerInterface` streams for reads, watches, checkpoints, audits, bulk dump, hot shards, queue metrics, and key-value store type are all served or dispatched from `storageServerCore()`.

## Risks and Edge Cases

- Atomic mutation conversion depends on eager reads when the old value is not present in latest MVCC. Missing or stale eager reads would convert an atomic op to the wrong set value.
- Clear-range expansion relies on VersionedMap clear-to markers and the trusted eager-read end. A too-short expansion can leave stale cleared data; a too-long expansion can remove unrelated data.
- `fetchKeys()` writes fetched blocks directly to storage before final MVCC catch-up. Its correctness depends on later availability metadata, durable-version waits, and cancellation cleanup staying in lockstep.
- Retrying fetchKeys after partial block writes is complex. The split path moves buffered updates across new shard ranges, assumes the right shard is still in `WaitPrevious`, and can become expensive if a range is split many times.
- Bulk-load SST ingestion has multiple fallback conditions: engine support, knob enablement, task range alignment, and file ranges contained in the assigned shard. Mismatches silently fall back to KV writes but still need cleanup and byte-sample correctness.
- In `fetchShard()`, the bulk-load branch asserts `bulkLoadTaskState.getDataMoveId() != moveInShard->dataMoveId()` even though the nearby comment says the metadata should have the same data-move ID. That looks like a high-risk assertion or comment mismatch for physical bulk load.
- `changeServerKeysWithPhysicalShards()` treats conflicting updates differently for TSS and normal SS, but both paths can throw data-move conflict errors. Lagging TSSs can be removed rather than recovered.
- Move-in update buffering can spill only after durable versions and uses byte limits when applying. Bugs in `lastRepliedVersion`, high-watermark persistence, or spill cleanup can duplicate or skip updates during physical shard movement.
- `updateStorage()` deliberately blocks at checkpoint, add-range, and remove-range barriers. Incorrect pending-range metadata can stall durable advancement or persist storage-engine range mappings at the wrong version.
- The durable commit path must coordinate `durableInProgress`, `durableVersionLock`, `changeDurableVersion()`, and eager reads. Advancing durable version while latest MVCC is partially loaded would expose inconsistent reads.
- Recovery reconstructs bulk-load metadata by exact or contained range matching. Partial overlap is logged as a warning-always mismatch; a recovered assignment with wrong metadata can fall back to normal movement or attempt the wrong bulk-load task.
- Non-shard-aware recovery clears every unavailable range after `changeServerKeys(CSK_RESTORE)`. Incorrect `newestAvailableVersion` restoration could delete useful data or preserve stale fetched data.
- Byte-sample recovery defers full sample loading and tracks clears in `byteSampleClears`. If the clear map grows too large, normal update processing pauses until recovery catches up.
- Private mutation handling assumes server-key range mutations arrive in begin/end pairs. Unexpected ordering, quarantine exceptions, or unsupported data-move type downgrades can change assignment behavior.
- `storageServerTerminated()` disposes persistent data on worker removal or recruitment failure but only closes on reboot/other errors. Misclassifying a shutdown error changes whether local storage survives.

## Test Signals

- Mutation tests should cover atomic op conversion for present, absent, and recently-cleared keys; compare-and-clear success/failure; clear expansion around existing clear-to markers; and set splitting of clear ranges.
- Durability tests should cover mutation-log pruning, freeable arena cleanup, `durableVersion` advancement, storage commit byte/clear-range limits, reboot-when-durable, and durable-version lock interactions with eager reads.
- Logical data-movement tests should cover assignment, unassignment, assign-empty, restore context, fetchKeys cancellation before and after `FetchingCF`, partial fetch splitting, retryable fetch errors, GRV fallback after transaction-too-old, and final availability transition.
- Bulk-load fetchKeys tests should cover SST ingestion success, fallback to KV writes, no matching files, empty ranges, file range mismatch, local sample-file processing, cleanup of local folders, and metrics task accounting.
- Physical shard move tests should cover `MovingIn` creation, checkpoint metadata fetch, checkpoint restore retry/fallback, bulk-load file metadata creation, update buffering/spilling, high-watermark progression, read-write-pending to read-write transition, and cleanup of persisted move-in records.
- Recovery tests should cover legacy and shard-aware formats, TSS pair/quarantine restoration, pending/deleting checkpoints, accumulative checksum restoration, bulk-load metadata exact/contained/mismatched ranges, unavailable-range clearing, and restored move-in shard actors.
- Checkpoint tests should verify that checkpoint creation blocks at the requested durable version, writes sample SST files when requested, persists complete/fail metadata, and schedules delete cleanup after persistence failure.
- Byte-sample tests should cover sampled set insertion, unsampled key removal, range clears, recovery chunking, `byteSampleClearsTooLarge` backpressure, and byte-metric notifications.
- Core service tests should cover read-serving actor dispatch, watch cases for same/different values and transaction-too-old retry, queue metrics, shard-state no-wait behavior, audit request validation, hot-shard selection, and disabled change-feed request logging.
- Sharded RocksDB consistency tests should exercise pending add/remove range quiescence, missing shard in SS/KV maps, mismatched shard IDs, and team shard count tracing.

### subset-b-008484: lines 12190-12732

# sources/storage-engines/foundationdb/fdbserver/storageserver/storageserver.actor.cpp lines 12190-12732

## Scope

This chunk covers the tail of `storageserver.actor.cpp`, from the retry loop used by memory-engine recovery to decide whether an old storage server can be removed, through storage-server interface re-registration, RocksDB log cleanup, the two `storageServer()` actor entry points for new recruitment and reboot recovery, and the local `versionedMapTest()` diagnostic. It is the final chunk for this oversized source file and depends on earlier chunks for the definitions of `StorageServer`, `storageServerCore()`, `StorageServerDisk`, shard state, durable-state serialization, byte-sample recovery, and many request handlers.

## Purpose

The code in this range wires a `StorageServer` object into cluster metadata and its local storage engine lifecycle. It decides how a process should rejoin after reboot, how a newly recruited storage server becomes durable and visible, how a TSS is reattached to its paired storage server, and how teardown should distinguish permanent removal from retryable reboot-style exits. It also adds a small background cleaner for RocksDB log files and a standalone versioned-map memory experiment.

The highest-level responsibilities are:

- Repeatedly check whether an in-memory storage server can be safely removed when recovery races with cluster metadata cleanup.
- Replace or refresh the `serverList`, `serverTag`, tag history, tag locality, and TSS mapping records used by commit proxies, data distribution, and clients.
- Gate when a `StorageServerInterface` advertises request acceptance during startup and recovery.
- Initialize local folders for checkpoints, fetched checkpoints, bulk dump, and bulk load state.
- Initialize, commit, mark durable, restore, or dispose the storage engine depending on whether this is a new recruitment or a rebooted server.
- Start `storageServerCore()` only after durable state and system-key registration are coherent.
- Ensure shutdown drains server-owned actors and local locks before `StorageServer self` leaves the stack.

## Important APIs, Types, and Functions

- `memoryStoreRecover(IKeyValueStore* store, Reference<IClusterConnectionRecord> connRecord, UID id)`: visible here from inside its retry loop. It creates a temporary client database and a `ReadYourWritesTransaction`, sets `PRIORITY_SYSTEM_IMMEDIATE` and `ACCESS_SYSTEM_KEYS`, calls `canRemoveStorageServer(tr, id)`, and waits/retries until cluster metadata confirms that the memory-backed server can be removed. It never completes for non-memory stores or missing connection records.
- `replaceInterface(StorageServer* self, StorageServerInterface ssi)`: actor used by normal storage servers during interface registration. It asks commit proxies for `GetStorageServerRejoinInfoReply`, writes the current `serverList` entry, updates locality/tag metadata if needed, prunes old tag history, then updates `self->tag`, `self->history`, and `self->allHistory`.
- `replaceTSSInterface(StorageServer* self, StorageServerInterface ssi)`: TSS-specific registration path. It reads the paired storage server's `serverTagKey`, fails with `worker_removed()` if the pair no longer exists, writes this TSS interface to `serverList`, and updates `tssMappingKeys` unless the TSS is quarantined.
- `storageInterfaceRegistration(StorageServer* self, StorageServerInterface ssi, Optional<Future<Void>> readyToAcceptRequests)`: common wrapper that either waits for an accept-ready future and calls `ssi.startAcceptingRequests()` or immediately calls `ssi.stopAcceptingRequests()`, then dispatches to the normal or TSS replacement path.
- `rocksdbLogCleaner(std::string folder)`: periodic actor that sanitizes the storage folder into a log prefix, scans `SERVER_KNOBS->LOG_DIRECTORY`, and deletes matching files older than `STORAGE_ROCKSDB_LOG_TTL`.
- `storageServer(...)` new-recruit overload: creates a new `StorageServer`, initializes storage, creates local directories, optionally calls `addStorageServer()`, sets the initial version/tag, calls `makeNewStorageServerDurable()`, replies to the recruiter, and runs `storageServerCore()`.
- `storageServer(...)` recovery overload: creates a `StorageServer` around an existing store, initializes/commits or races that commit with `memoryStoreRecover()`, restores durable state, validates TSS identity, re-registers the interface, and runs `storageServerCore()`.
- `versionedMapTest()`: local diagnostic that mutates a `VersionedMap<int,int>` at many versions and prints node size, allocation size, distinct key count, and memory usage.

Important data and integration types in the chunk include `IKeyValueStore`, `StorageServerInterface`, `Tag`, `Version`, `ReplyPromise<InitializeStorageReply>`, `AsyncVar<ServerDBInfo>`, `ReadYourWritesTransaction`, `Transaction`, `CommitProxyInfo`, `GetStorageServerRejoinInfoRequest/Reply`, `KeyBackedMap<UID, UID>`, `ActorCollection`, and `VersionedMap`.

## Control Flow

`memoryStoreRecover()` repeatedly starts or reuses a RYW transaction against the cluster connection record. On each pass it sets system/immediate options and calls `canRemoveStorageServer()`. If removal is not yet safe, it waits for `REMOVE_RETRY_DELAY`, resets the transaction, traces `RemoveStorageServerRetrying`, and tries again. Retryable transaction errors flow through `tr->onError()`. Completion of this actor indicates the memory store can be disposed; otherwise the storage-engine commit can win the race in the recovery overload.

`replaceInterface()` loops until it can obtain rejoin information from a live commit proxy and commit the replacement metadata. Each iteration captures `self->db->onChange()` and the current commit proxy list. If no commit proxies are known it waits only for database-info changes. When a proxy replies, the function pins the transaction to `rep.version`, sets immediate and lock-aware options, adds read conflict ranges over the server-list/tag/tag-history/locality keys, and writes the current `serverList` value. If the server moved localities, it updates the tag-locality map. If a new tag is assigned, it uses `FIRST_IN_BATCH`, adds a tag-conflict read/write range, writes `serverTagKeyFor(ssi.id())`, and appends old tag history via `SetVersionstampedKey`. It also clears stale tag-history entries older than the storage server's durable version. After commit, in-memory tag/history fields are updated and traced; a buggify path can force `please_reboot()` when history is present.

`replaceTSSInterface()` is simpler but stricter. It loops on transaction errors, reads the pair's `serverTagKey`, and treats a missing pair as permanent worker removal. It then writes the TSS interface to `serverList` and conditionally writes the pair-to-TSS map. On commit it copies the pair's decoded tag into `self->tag`, because a TSS shadows its pair's tag rather than owning an independent server tag.

`storageInterfaceRegistration()` first controls whether the interface is accepting requests. New servers pass a future that is only set when the outer startup path allows serving. Recovery first invokes this helper without a future, intentionally registering a non-accepting interface to refresh metadata before core startup; later it starts the long-lived accepting registration actor using `self.registerInterfaceAcceptingRequests.getFuture()`.

The new-recruit `storageServer()` overload follows a staged startup:

1. Construct `StorageServer self`, preserve shard-awareness, set initial cluster version, and set TSS pair state if applicable.
2. Initialize server key prefix and storage-related folder paths, then add `rocksdbLogCleaner()`.
3. Call `self.storage.init()` and `self.storage.commit()` to establish an initialized local store.
4. Create checkpoint/fetched-checkpoint folders and clear bulk dump/load folders.
5. If `seedTag == invalidTag`, open the interface for accepting requests, send the internal readiness promise, call `addStorageServer()`, assign the returned tag, and set the initial version to `addedVersion - 1` for normal servers or `tssSeedVersion` for TSS.
6. If a seed tag was provided, use it directly.
7. Persist the fact that this is a new durable storage server with `makeNewStorageServerDurable(self.shardAware)` and commit again.
8. Start the long-lived interface-registration actor, send `InitializeStorageReply`, clear byte-sample recovery to ready state, and run `storageServerCore()`.

Any error before the recruitment reply sends `recruitment_failed()` to the recruiter. All errors halt `ssLock`, clear `moveInShards`, call `storageServerTerminated()`, cancel `ssCore`, drop background actors, yield once, and either return for terminal removal-style errors or rethrow for higher-level process handling.

The recovery `storageServer()` overload follows a different sequence:

1. Construct `StorageServer self`, derive folder paths, create missing checkpoint folders with warning traces, clear bulk dump/load folders, and add the RocksDB log cleaner.
2. Initialize storage, then race `self.storage.commit()` with `memoryStoreRecover()`. A memory-recovery win means the server was removed from cluster metadata before recovery could finish; the code traces `DisposeStorageServer` and throws `worker_removed()`.
3. Restore durable server state with `restoreDurableState()`. If the store is not a durable storage server, signal `recovered` and return.
4. Validate TSS identity: for TSS recovery, the durable `tssPairID` from the store becomes source of truth for `ssi.tssPairID`; for non-TSS, the store must not report TSS state.
5. Rebuild `self.sk`, trace the restored version, and send `recovered`.
6. Synchronously perform a non-accepting `storageInterfaceRegistration()` and surface any registration error.
7. Start the long-lived accepting registration actor, then run `storageServerCore()`.

Recovery shutdown mirrors new-server shutdown, with additional cancellation of `byteSampleRecovery` if it is still valid and a final attempt to set the `recovered` promise.

## State and Persistence Behavior

- Cluster metadata writes are concentrated in system keys: `serverListKeyFor(ssi.id())`, `serverTagKeyFor(ssi.id())`, `serverTagHistoryKeyFor(ssi.id())`, `tagLocalityListKeyFor(dcId)`, and `tssMappingKeys`.
- `replaceInterface()` uses read conflicts over metadata that must be stable across rejoin, and a write conflict on `serverTagConflictKeyFor(newTag)` when assigning a new tag. This protects against duplicate tag ownership and locality-list races.
- Tag history persists old tags using a versionstamped key mutation, and stale history before `self->version.get()` is cleared so future recovery/rejoin logic only sees relevant tag epochs.
- `self->tag`, `self->history`, and `self->allHistory` are volatile mirrors of committed metadata. They are assigned only after the metadata transaction commits.
- `replaceTSSInterface()` persists a TSS's current network interface but derives `self->tag` from the paired storage server. The `tssMappingKeys` entry is suppressed while the TSS is quarantined, which keeps quarantined TSS instances from being selected as live shadows.
- New-server startup persists local storage state in two phases: an initial storage commit after `init()`, then `makeNewStorageServerDurable()` followed by another commit after tag/version decisions are made.
- Recovery uses `restoreDurableState()` as the local source of truth for server identity, version, TSS state, and other durable fields written by earlier chunks. If no durable storage-server marker exists, recovery reports success to the caller but does not run core.
- The local filesystem state under `folder` contains checkpoint, fetched-checkpoint, bulk-dump, and bulk-load subfolders. Startup creates checkpoint directories and clears bulk transfer folders so stale bulk artifacts do not survive process restart.
- RocksDB log cleanup is external to the key-value store state. It matches files in the global log directory by a sanitized folder-derived prefix and deletes them after a knob-defined TTL.
- Shutdown calls `storageServerTerminated()` outside this chunk to decide between `persistentData->dispose()` and `persistentData->close()` for removal/recruitment failure versus reboot-style exits.

## Dependencies and Integration Points

- Commit proxies provide `getStorageServerRejoinInfo`, including the rejoin version, tag, tag history, possible new locality, and possible new tag. Normal server re-registration cannot complete without a live commit proxy set in `ServerDBInfo`.
- System-key encoders from the management/metadata layer define server-list, server-tag, server-tag-history, locality-list, and TSS mapping keys. Correct encoding compatibility is required for commit proxies, data distribution, clients, and TSS routing.
- `ReadYourWritesTransaction` is used for TSS map writes and memory-store removal checks because those paths use higher-level key-backed structures and normal transaction retry handling.
- `Transaction` is used directly in `replaceInterface()` to pin the metadata transaction to the commit proxy's supplied version and to set low-level options such as `FIRST_IN_BATCH`.
- `StorageServerInterface` owns the RPC endpoints registered in `serverList`. `startAcceptingRequests()` and `stopAcceptingRequests()` change advertised readiness before serializing the interface value.
- `StorageServerDisk` or the storage wrapper behind `self.storage` supplies `init()`, `commit()`, `makeNewStorageServerDurable()`, `restoreDurableState()`, `getKeyValueStoreType()`, and shard-awareness state.
- `storageServerCore()` is the main serving actor from earlier chunks; this range ensures it starts only after cluster metadata and local durable state are prepared.
- `ActorCollection` owns background actors such as `rocksdbLogCleaner()` and actors started by the core. Assigning `ActorCollection(false)` cancels them during teardown.
- `SERVER_KNOBS` controls retry delay, RocksDB log cleanup delay, log TTL, and log directory; simulation `buggify()` can force history-related reboot behavior.

## Risks and Edge Cases

- `replaceInterface()` deliberately races `self->db->onChange()` against commit-proxy work. If proxy info changes while a transaction is in flight, the actor may abandon that attempt and loop. Bugs here can leave a storage server with stale interface data or an incorrect tag history.
- The metadata transaction is set to `rep.version`. If `GetStorageServerRejoinInfoReply` is stale or inconsistent with system keys, conflict ranges and transaction retry behavior must catch the mismatch.
- New tag assignment is high risk: duplicate or lost tags can corrupt log routing. The explicit `serverTagConflictKeyFor(newTag)` read/write conflict and `FIRST_IN_BATCH` option are important safety signals.
- The `rep.history.back().first < self->version.get()` cleanup assumes history is ordered in a way where `back()` is the oldest or cleanup boundary is otherwise meaningful. A change to history ordering would make this pruning dangerous.
- TSS recovery depends on the durable store's TSS marker rather than the incoming interface alone. If the durable marker and process recruitment state diverge, the assertions deliberately crash rather than silently register the wrong type of server.
- A TSS whose pair was removed while it was down throws `worker_removed()`. This is correct for cleanup, but the path must ensure the local store is disposed/closed consistently by `storageServerTerminated()`.
- The memory-store recovery race is subtle: if `memoryStoreRecover()` returns before `self.storage.commit()`, recovery treats the server as removed. If it never returns for a valid server, the storage commit should win. Changes to this race can affect in-memory engine restart semantics.
- Startup clears bulk dump/load directories unconditionally with `ignoreError=false`; filesystem permission or stale-file problems become startup failures.
- `rocksdbLogCleaner()` matches log files by substring of a sanitized folder prefix. A too-broad prefix could delete unrelated RocksDB logs; a too-narrow prefix could leak logs. It also assumes file modification time is available and meaningful.
- Both `storageServer()` overloads keep `StorageServer self` on the actor stack. Teardown must halt locks and cancel child actors before returning or rethrowing to avoid child actors using invalid stack memory.
- The new-server path starts accepting requests before `addStorageServer()`, but only after the interface is created for recruitment. This ordering relies on the broader recruitment protocol preventing client traffic before server-list metadata is committed.
- `recruitReply` must be completed exactly once. The catch block sends `recruitment_failed()` only if it has not already sent a success reply.

## Test Signals

- New storage server recruitment should be tested for invalid versus seeded tags, normal versus TSS servers, correct initial version selection, durable marker persistence, and `InitializeStorageReply` contents.
- Reboot recovery tests should cover existing durable servers, stores without durable storage-server state, TSS durable-state recovery, non-TSS assertions, and `recovered` promise completion on success and failure.
- Interface registration tests should cover commit-proxy unavailability, `ServerDBInfo` changes while waiting, conflict retries, new locality creation, new tag assignment, tag-history insertion, tag-history pruning, and buggified reboot from non-empty history.
- TSS registration tests should cover pair tag lookup, missing pair removal, quarantine suppressing `tssMappingKeys`, non-quarantined mapping creation, and assigning the pair tag to `self->tag`.
- Memory-engine recovery tests should cover `canRemoveStorageServer()` returning false several times, transaction retry errors through `onError()`, the race where memory recovery wins and triggers `worker_removed()`, and non-memory stores never taking the removal path.
- Filesystem tests should cover missing checkpoint directories on reboot, clear failures for bulk folders, checkpoint/fetched-checkpoint creation for new stores, and safe handling of folder names used by the RocksDB log cleaner.
- Shutdown tests should inject `worker_removed`, `recruitment_failed`, `please_reboot`, actor cancellation, and generic internal errors to verify close/dispose behavior, core cancellation, actor collection cancellation, lock halt, move-in shard clearing, and error propagation.
- Observability expectations include `StorageServerInitProgress`, `StorageServerInit`, `StorageServerRebootStart`, `SSTimeRestoreDurableState`, `StorageServerReboot`, `StorageServerStartingCore`, `SSTag`, `SSHistory`, `RemoveStorageServerRetrying`, `CleanUpRocksDBLogs`, and `DeleteRocksDBLog` traces.

## Unresolved Cross-Chunk References

- `StorageServer` fields and `self.storage` durable-state semantics are defined earlier in the file and are needed to fully audit `makeNewStorageServerDurable()` and `restoreDurableState()`.
- `storageServerTerminated()` begins immediately before this chunk and controls final `close()` versus `dispose()` behavior.
- `storageServerCore()` and request-serving actors are in earlier chunks; this chunk only shows when core starts and how it is cancelled.
- `addStorageServer()`, `canRemoveStorageServer()`, `serverListValue()`, `decodeServerTagValue()`, and system-key helpers are external integration points whose exact invariants are not shown here.
