# sources/storage-engines/foundationdb/fdbclient/NameLineage.cpp

## Purpose

`NameLineage.cpp` is the registration translation unit for the actor-name lineage collector. It includes `NameLineage.h` and defines one unnamed-namespace static `NameLineageCollector nameLineageCollector;`. Constructing this static object registers the collector with the actor lineage sampling framework through the `IALPCollector` base constructor path.

## Important APIs, types, and functions

The only concrete symbol in this file is the internal-linkage `nameLineageCollector`. Its type is defined in `NameLineage.h`; the collector reads the `NameLineage::actorName` property from an `ActorLineage` and returns it as `std::string_view` when present.

There are no callable functions, exported classes, or explicit control methods in this `.cpp`. Its behavior relies on C++ static initialization.

## Control flow

At program or shared-library load time, the static `NameLineageCollector` object is constructed. The base collector infrastructure in `ActorLineageProfiler.h` exposes `IALPCollectorBase` and `SampleCollector`; the collector constructor path is expected to add this collector to the profiler's collector list. During sampling, the profiler can then invoke the collector implemented in the header.

## State and persistence behavior

The file creates one process-local singleton-like static object. It does not persist data to disk and does not own sampled lineage data. Its state is simply collector registration lifetime; the object exists until process or library teardown.

## Dependencies and integration points

The file depends on `NameLineage.h`, which depends on `fdbclient/ActorLineageProfiler.h`. It integrates with `ActorLineageProfiler.cpp`, where sampled actor lineages populate `NameLineage::actorName`, and with special-key or profiler ingestion paths that expose actor-lineage samples.

One notable integration detail is that `NativeAPI.actor.cpp` also defines a `NameLineageCollector nameLineageCollector` at file scope. That provides registration when native API code is linked; this standalone `.cpp` provides registration for builds or link paths that include this translation unit.

## Risks and edge cases

The file's only behavior depends on static initialization and linker inclusion. If the object file is not linked, the collector is not registered. If multiple translation units register the same collector name, downstream sample collection must tolerate duplicate collectors or build configurations must avoid duplicate registration. Static initialization ordering also matters if collector registration assumes the profiler singleton is ready during construction.

## Test signals

There is no local unit test. Indirect test signals are actor-lineage profiler tests or special-key actor-lineage queries that include an `"Actor"` field derived from `NameLineage::name`. Linkage-sensitive coverage should verify that the collector appears in binaries that rely on this `.cpp` rather than `NativeAPI.actor.cpp`.
