# sources/storage-engines/foundationdb/fdbclient/AnnotateActor.cpp

## Purpose

`AnnotateActor.cpp` provides the single storage definition for the global `samples` map declared by the actor annotation/profiling headers. It exists to satisfy linkage for code that records sample getters by wait state.

## Important APIs, Types, and Functions

- `samples` is a `std::map<WaitState, std::function<std::vector<Reference<ActorLineage>>()>>`.
- `WaitState` and `ActorLineage` are declared in `fdbclient/AnnotateActor.h`.

## Control Flow

There is no runtime control flow in this file. It includes the header and defines the global object.

## State and Persistence Behavior

The `samples` map is process-local mutable global state. It does not persist to the database or disk. Other translation units can register or read sampling callbacks through the declaration in the header.

## Dependencies and Integration Points

The file links the actor annotation infrastructure with the lineage profiler. It depends entirely on `AnnotateActor.h` for type definitions.

## Risks and Edge Cases

Global mutable state can introduce initialization-order and thread-safety concerns if modified concurrently. The file itself has no locking; synchronization must be provided by users of the map or by initialization discipline.

## Test Signals

There are no direct tests in the visible subset. Compile/link success is the main signal. Runtime profiling tests would indirectly verify that callbacks registered in `samples` are visible across translation units.
