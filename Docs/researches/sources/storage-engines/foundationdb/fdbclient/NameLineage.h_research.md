# sources/storage-engines/foundationdb/fdbclient/NameLineage.h

## Purpose

`NameLineage.h` defines the actor-name property used by FoundationDB's actor lineage profiler and the collector that serializes that property into sampled profiler output. It is a small bridge between `ActorLineage` property storage and the generic actor-lineage collector framework.

## Important APIs, types, and functions

`NameLineage` derives from `LineageProperties<NameLineage>`. It declares `static constexpr std::string_view name = "Actor"sv`, which is the collector/property name exposed in collected samples, and a single property field `const char* actorName`.

`NameLineageCollector` derives from `IALPCollector<NameLineage>`. Its constructor just delegates to `IALPCollector`. Its `collect(ActorLineage* lineage)` override calls `lineage->get(&NameLineage::actorName)`. If the property exists, it returns `std::string_view(*str, std::strlen(*str))` wrapped in `std::any`; otherwise it returns an empty `std::optional`.

## Control flow

The header provides inline collector logic. A translation unit creates a `NameLineageCollector` static object, which registers the collector. When the actor-lineage profiler collects a sample, `SampleCollectorT` iterates registered `IALPCollectorBase` objects. For this collector, `collect()` reads the actor-name property from the sampled `ActorLineage` and returns it under the `NameLineage::name` key.

The property is populated elsewhere. `ActorLineageProfiler.cpp` modifies `NameLineage::actorName` from a lineage pointer's `actorName()` before submitting collection work to the profiler context. Actor annotation and special-key paths then consume collected samples.

## State and persistence behavior

The header does not allocate persistent storage. The `actorName` value is a raw `const char*` stored as a lineage property, so its lifetime must be valid for the collection window. The collector returns a `std::string_view` rather than copying into `std::string`, so downstream handling must not outlive the underlying actor name unless it copies the value during serialization or ingestion.

## Dependencies and integration points

The header includes `<string_view>` and `fdbclient/ActorLineageProfiler.h`. It relies on the Flow `ActorLineage` property API, `LineageProperties`, `IALPCollector`, and the profiler's sample collector registry. Integration points include `ActorLineageProfiler.cpp`, `NativeAPI.actor.cpp`, `NameLineage.cpp`, `SpecialKeySpace.cpp` actor-lineage APIs, and profiler ingestors such as FluentD.

## Risks and edge cases

The collector assumes the stored `const char*` is non-null and NUL-terminated when present. `std::strlen(*str)` will read until a terminator, so invalid lifetime or non-terminated actor names would be unsafe. Returning `std::string_view` in `std::any` is efficient but requires consumers to copy promptly if samples cross thread or lifetime boundaries.

Because registration is performed by static collector instances outside this header, including the header alone does not register the collector. Builds must link a translation unit that instantiates `NameLineageCollector`.

## Test signals

There is no direct unit test in this header. Indirect signals should come from actor-lineage profiler sampling tests, special-key actor-lineage output tests, or ingestion tests that assert the `"Actor"` field is emitted when a sampled lineage has an actor name and omitted when it does not.
