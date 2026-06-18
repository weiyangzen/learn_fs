# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/StackLineage.h

## Purpose
`StackLineage.h` declares a collector for actor lineage stack traces. It bridges actor lineage profiler data into a vector of string views suitable for profiling consumers.

## Important APIs, Types, And Functions
- `getActorStackTrace()` is an external function returning Flow `StringRef` stack frames.
- `StackLineageCollector` inherits `IALPCollector<StackLineage>`.
- `collect(ActorLineage*)` asks the lineage for stack data keyed by `StackLineage::actorName`, converts each `StringRef` to `std::string_view`, and returns it in `std::any`.

## Control Flow And State
The collector is stateless. Each `collect()` call obtains a vector from the provided lineage and builds a vector of views over the returned string data.

## Persistence And External State
No persistent state exists. Returned string views depend on the lifetime of the underlying lineage/string storage.

## Dependencies And Integration Points
It depends on Flow and `ActorLineageProfiler.h`. It integrates with process/actor lineage reporting, including special key or RPC surfaces that expose profiling samples.

## Risks And Edge Cases
The conversion to `std::string_view` is non-owning; consumers must not retain views beyond the backing string lifetime. The collector assumes the provided `ActorLineage*` is valid. Empty or missing stack data returns an empty vector inside `std::any`.

## Test Signals
Tests should cover collecting from lineages with multiple frames, empty stacks, lifetime expectations for returned views, and integration with actor lineage serialization/reporting paths.
