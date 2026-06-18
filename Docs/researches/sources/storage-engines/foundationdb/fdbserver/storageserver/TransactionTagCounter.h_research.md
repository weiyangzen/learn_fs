# sources/storage-engines/foundationdb/fdbserver/storageserver/TransactionTagCounter.h

## Purpose
`TransactionTagCounter.h` declares the storage-server helper that measures recent read load by transaction tag. Storage servers call it from read request paths to attribute request byte cost to the optional `TagSet` carried by client requests, roll the measurements at a configured interval, and expose the busiest tags to storage queuing metrics so ratekeeper and status surfaces can reason about tag-specific read pressure.

The header is intentionally narrow: it hides the implementation behind `PImpl<class TransactionTagCounterImpl>` so storage-server users do not include the implementation's priority queue, tag map, tracing, and knob dependencies. The public API is the lifecycle and interval interface needed by `storageserver.actor.cpp`.

## Important APIs, Types, and Functions
- `TransactionTagCounter(UID thisServerID, int maxTagsTracked, double minRateTracked)` constructs the counter for one storage server. `thisServerID` is used in trace events, `maxTagsTracked` bounds the retained top-K tag set, and `minRateTracked` filters low-rate tags.
- `~TransactionTagCounter()` is out-of-line because the implementation type is opaque at the declaration site.
- `void addRequest(Optional<TagSet> const& tags, int64_t bytes)` records one read request's cost for the current interval. It accepts absent tags, which still contribute to total interval cost in the implementation but do not create per-tag entries.
- `void startNewInterval()` finalizes the current interval, stores the previous interval's busiest tags, emits trace events, and resets current counters.
- `std::vector<BusyTagInfo> const& getBusiestTags() const` returns the retained busiest tags from the last completed interval. `BusyTagInfo` and `TagSet` come from `fdbclient/StorageServerInterface.h` and `fdbclient/TagThrottle.h`.

## Control Flow
`StorageServer` embeds a `TransactionTagCounter` member. During `storageServerCore`, the server calls `startNewInterval()` once, then schedules a recurring call every `SERVER_KNOBS->TAG_MEASUREMENT_INTERVAL`. Read request actors call `addRequest()` after responding or erroring where the byte cost is known. Call sites include `getValueQ`, `getKeyValuesQ`, `getMappedKeyValuesQ`, `getKeyValuesStreamQ`, and `getKeyQ`; the byte estimate is usually returned bytes, with some path-specific additions such as key size for `getValue`.

At each interval boundary, the implementation computes per-tag rates from accumulated sampled read operation cost divided by elapsed wall-clock time, filters tags below `minRateTracked`, keeps at most `maxTagsTracked` using a min-priority queue, and saves that vector as `previousBusiestTags`. `getQueuingMetrics()` later copies `self->transactionTagCounter.getBusiestTags()` into `StorageQueuingMetricsReply::busiestTags`, integrating the previous interval into queue metrics responses.

## State and Persistence Behavior
The header exposes no persistent state. Runtime state lives only inside `TransactionTagCounterImpl`: server ID, a `TransactionTagMap<double>` of interval costs, total interval cost, interval start time, configuration bounds, a vector of previous busy tags, and an event-cache holder for busiest-read-tag tracing. State resets on process restart and is not written to the storage engine.

The implementation bills each tagged request by `getReadOperationCost(bytes)` and scales per-tag cost by `CLIENT_KNOBS->READ_TAG_SAMPLE_RATE`, while total interval cost is kept unscaled. This makes the busy-tag rate an estimate based on sampled tagged reads. `fractionalBusyness` is derived from the tag cost over interval total cost and is capped at `1.0`. Untagged reads increase total cost but not per-tag cost, lowering fractional busyness for tagged traffic when untagged traffic is present.

## Dependencies and Integration Points
The declaration depends on `fdbclient/PImpl.h` for opaque ownership, `fdbclient/StorageServerInterface.h` for `UID` and `BusyTagInfo`, and `fdbclient/TagThrottle.h` for transaction tag types. The implementation depends on `NativeAPI.actor.h` for read-cost calculation, client knobs, Flow time, `TraceEvent`, and FoundationDB test macros.

The main integration points are the storage-server read actors and `StorageQueuingMetricsRequest` handling in `storageserver.actor.cpp`. Ratekeeper consumes storage queuing metrics from each storage server, so the data exposed by this counter participates in read tag throttling and cluster status observability. Trace events `BusiestReadTag` and `BusyReadTag` are also integration points for diagnostics and status event caches.

## Risks and Edge Cases
The first interval is intentionally ignored because `intervalStart` is zero until the initial `startNewInterval()` call. If the recurring interval is not started, `getBusiestTags()` remains empty even if reads call `addRequest()`.

The returned vector is a const reference to internal state, so callers must not retain it beyond the counter lifetime or expect it to remain stable across `startNewInterval()`. Storage-server code currently copies it into a reply promptly, which matches the contract.

Cost accounting is approximate. Some request paths undercount true scanned bytes, and `getKeyValuesStreamQ` appears to call `addRequest()` inside the stream loop using `resultSize` without updating that local variable in the visible loop, then calls it again after the loop. That is an integration risk for read tag throttling accuracy rather than a persistence risk. The top-K vector is not sorted highest-first when drained from the min-priority queue, so implementation code explicitly scans for the busiest tag when emitting the single `BusiestReadTag` trace. Any consumer that assumes the vector is sorted by descending rate would be fragile.

If `CLIENT_KNOBS->READ_TAG_SAMPLE_RATE` is zero, interval finalization suppresses calculations to avoid division by zero. However, `addRequest()` still divides per-tag cost by the sample rate when tags are present in the implementation, so the surrounding configuration should not allow tagged sampled reads with a zero sample rate between interval ticks.

## Test Signals
`TransactionTagCounter.cpp` contains focused unit tests. `/fdbserver/TransactionTagCounter/IgnoreBeyondMaxTags` verifies that the counter keeps only the configured number of busiest tags and drops lower-rate tags. `/fdbserver/TransactionTagCounter/IgnoreBelowMinRate` verifies that low-rate tags are filtered out. Runtime signals include `BusiestReadTag` and `BusyReadTag` trace events, non-empty `StorageQueuingMetricsReply::busiestTags` during tagged read workloads, and ratekeeper behavior when read tag throttling is enabled.
