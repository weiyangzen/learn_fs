# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDRelocationQueue.actor.cpp`

## Purpose

This actor implementation is the core scheduler and executor for FoundationDB data-distribution relocations. It receives `RelocateShard` requests, coalesces/overwrites queued intent by key range, fetches source servers, throttles launches by source and destination server busyness, selects destination teams, invokes `moveKeys()`, updates shard-location metadata, handles data-move cancellation/cleanup, and runs background disk/read rebalance loops.

## Important APIs, Types, and Functions

- `RelocateData` wraps `RelocateShard` with queue/runtime metadata: key range, priority, reason, data-move reason/id, source and destination IDs, work factor, cancellability, parent split range, trace interval, optional restored `DataMove`, and optional bulk-load task.
- `ParallelTCInfo` adapts multiple `IDataDistributionTeam` instances into a single aggregate team-like object for metrics/in-flight accounting across regions.
- `Busyness` maintains fixed-point work ledgers by priority bucket; `canLaunch()`, `addWork()`, and `removeWork()` gate source and destination concurrency.
- `getSourceServersForRange()` reads source server membership through `IDDTxnProcessor::getSourceServersForRange()`.
- `DDQueue::queueRelocation()` merges incoming relocation intent into `queueMap`, truncates or cancels overlapping queued work, and starts source-fetch actors.
- `DDQueue::launchQueuedWork()` chooses launchable queued work, cancels contained in-flight actors, assigns data-move IDs, updates in-flight maps, applies busyness, and starts `dataDistributionRelocator()`.
- `cancelDataMove()` and `enqueueCancelledDataMove()` serialize cleanup of existing data-move metadata via `cleanUpDataMove()`.
- `dataDistributionRelocator()` is the main move actor. It cleans conflicting data moves, validates bulk-load state, retrieves metrics, repeatedly selects healthy destination teams, updates `ShardsAffectedByTeamFailure`, builds `MoveKeysParams`, runs `txnProcessor->moveKeys()`, tracks data-transfer completion, and finalizes physical-shard/bulk-load state.
- `rebalanceReadLoad()`, `rebalanceTeams()`, `BgDDLoadRebalance()`, and `getSrcDestTeams()` implement background mountain-chopper/valley-filler movement for disk and read load.
- `pipelineGateActor()` limits non-urgent relocation intake by `DD_MAX_PIPELINE_MOVES` while allowing cancellations and high-priority health moves to pass.
- `DDQueueImpl::run()` is the top-level actor loop for queue events, source fetch completions, data-transfer completions, relocation completions, metrics logging, background rebalancers, pipeline gate errors, and unhealthy relocation count requests.

## Control Flow

Incoming `RelocateShard`s pass through `pipelineGateActor()` unless they are cancellations or high-priority health moves. The run loop dispatches restore moves directly, cancellation messages to cleanup, and normal moves to `queueRelocation()`. `queueRelocation()` overlays the requested range in `queueMap`, cancels affected source-fetch actors, preserves higher health/boundary priorities when replacing queued work, and schedules new source-server fetches. Once sources are fetched, `completeSourceFetch()` indexes the relocation by each source server and triggers `launchQueuedWork()`.

Launch checks combine candidate relocations from affected sources or ranges. The queue refuses to launch if an overlapping in-flight move with adequate priority should continue, or if source busyness cannot accommodate the move after considering cancellable contained work. Launching removes queued entries, cancels contained in-flight actors, optionally cleans previous data moves, writes a new in-flight `RelocateData`, charges source busyness, increments active counts, and starts a relocator actor.

The relocator first makes the in-flight entry non-cancellable when location metadata is encoded, waits for prior cleanup, possibly revalidates bulk-load task metadata, and assigns or finalizes a data-move ID. It fetches shard metrics and optional parent metrics for split diagnostics. Destination team selection loops over team collections, using restore-specified teams or `GetTeamRequest` policies driven by priority, read rebalance, bulk load, physical-shard requirements, and "true best" preferences. If teams are unavailable or destinations are too busy, it delays and retries; restore/bulk-load cases can eventually fail with `data_move_dest_team_not_found`.

After destination selection, the actor updates `ShardsAffectedByTeamFailure::moveShard()` for new moves, charges data/read in-flight to destination teams, charges destination busyness, emits relocation decision traces, and calls `moveKeys()`. The move may complete in two phases when cross-DC optimization initially moves to one remote server and later expands to all extra IDs. Data-transfer completion and relocation completion are signaled separately, allowing busyness to be released before the whole actor finishes. On success it clears completed data-move tracking, records bytes/rate, calls `finishMove()`, updates `PhysicalShardCollection` when enabled, terminates bulk-load task state, and returns. Retryable move-key errors release destination accounting and loop; non-cancel errors propagate through the queue error promise.

## State and Persistence Behavior

Most queue state is in memory: `queueMap`, per-source `queue`, `fetchingSourcesQueue`, `fetchKeysComplete`, `inFlight`, `inFlightActors`, `dataMoves`, source/destination busyness maps, priority counters, pipeline counters, and moving-window byte-rate stats. Durable/persistent effects are mediated through `IDDTxnProcessor` and core move-key helpers: source lookup, data-move cleanup, `moveKeys()`, DD ignore switch reads, health metrics, and bulk-load task reads/updates. When `SHARD_ENCODE_LOCATION_METADATA` is enabled, data-move IDs are stored in metadata flows and `dataMoves` protects against overlapping cleanup/write races. Physical-shard updates remain in the in-memory `PhysicalShardCollection` but are keyed by data-move IDs derived from physical shard IDs.

## Dependencies and Integration Points

This file integrates with `DataDistributionTeam` for team selection and load metrics, `DDTxnProcessor` for database/system-key operations, `MoveKeys` for actual metadata changes, `ShardsAffectedByTeamFailure` for shard/team ownership maps, `PhysicalShardCollection` for physical shard reuse/transition, `BulkLoadTaskCollection` for bulk-load scheduling, server knobs for priorities/throttles, Flow actor primitives, trace/event-cache infrastructure, and simulation knobs/buggify paths. It also serves metrics requests from `DDShardTracker` through `getShardMetrics` and `getTopKMetrics` streams during relocation and rebalance decisions.

## Risks and Edge Cases

Correctness is sensitive to non-atomic updates between in-flight actor maps, `dataMoves`, and physical-shard maps; the file contains TODO comments around split-brain risk and future assertions. Queue replacement must preserve health/boundary priority or urgent recovery can be delayed. Source lists can become stale between fetch and launch. Busyness accounting must be released exactly once across transfer-complete, retry, cancellation, and error paths. Cross-region best-team readiness has a no-wait requirement before `moveShard()` to avoid missing failure notifications. Bulk-load tasks can become outdated after source launch but before cleanup completes, causing fallback or task failure. Physical shard selection can choose full or unhealthy remote teams and must force re-selection. Pipeline control deliberately bypasses urgent moves, so health storms can still produce high activity.

## Test Signals

The file includes `/DataDistribution/DDQueue/ServerCounterTrace`, which exercises periodic server-counter tracing with randomized teams/reasons/count types. Broader behavioral coverage likely comes from simulation workloads and datadistributor integration tests rather than local unit tests. Trace signals are extensive: queue size changes, pipeline full/clear, relocation begin/end, best-team stuck, destination busy, data-move conflicts, move rates, rebalance decisions, bulk-load state, and physical-shard retry counters.
