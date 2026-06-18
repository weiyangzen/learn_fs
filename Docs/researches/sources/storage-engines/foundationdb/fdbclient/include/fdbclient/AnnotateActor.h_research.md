# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/AnnotateActor.h

Purpose: RAII helper for marking actor lineage as currently waiting/running for sampling profiler collection.

Important APIs and types: `AnnotateActor` inserts a `LineageReference` into `g_network->getActorLineageSet()` when `ENABLE_SAMPLING` is defined and erases it in the destructor. It is non-copyable; move assignment transfers the index/set flag. `WaitState` enumerates `Disk`, `Network`, and `Running`, with `to_string` conversion.

State and persistence: state is transient profiler membership in the network's actor lineage set. No durable persistence.

Dependencies and integration: includes Flow runtime/network headers. `ActorLineageProfiler.h` consumes `WaitState` and `ActorLineage` sampling concepts. Under non-sampling builds, the helper mostly compiles away.

Risks: move construction is deleted but move assignment exists; misuse can leave an annotation unset or transferred unexpectedly. Destruction must run to erase the lineage index. The `using namespace std::literals` in a header is justified by the comment but still expands namespace exposure.

Test signals: sampling builds and profiler tests validate insertion/removal behavior; no local unit tests.
