# `sources/storage-engines/foundationdb/fdbserver/datadistributor/DDSharedContext.cpp`

## Purpose

This file provides the constructor/destructor definitions for `DDSharedContext`, the reference-counted object that carries common data-distributor state shared by tracker, relocation queue, team collections, and related DD components.

## Important APIs and Types

- `DDSharedContext::DDSharedContext()` leaves members at their header defaults.
- `DDSharedContext::DDSharedContext(const DataDistributorInterface& iface)` delegates to the UID constructor using `iface.id()` and then stores the full interface.
- `DDSharedContext::DDSharedContext(UID id)` allocates a shared `DDEnabledState`, stores the distributor ID, and creates a `ShardsAffectedByTeamFailure` instance.
- `DDSharedContext::~DDSharedContext()` is defaulted in the implementation file, allowing smart/reference-counted members to clean themselves up.

The associated header exposes `ddEnabledState`, `interface`, `ddId`, `MoveKeysLock`, `trackerCancelled`, `configuration`, `shardsAffectedByTeamFailure`, tracker/queue/team-collection references, and convenience methods such as `id()`, `markTrackerCancelled()`, `usableRegions()`, and `isDDEnabled()`.

## Control Flow

Construction is intentionally simple. The interface constructor is the production path when a `DataDistributorInterface` already exists; it ensures `ddId` and the stored interface are consistent. The UID constructor is the lower-level initializer for tests or setup paths that only have an ID. No actor is started here; consumers attach `DataDistributionTracker`, `DDQueue`, and team collection references after constructing the shared context.

## State and Persistence Behavior

The context is in-memory shared state. It does not read or write database keys. The `DDEnabledState` is heap-owned by a `unique_ptr` and intentionally stable because other components, including snapshot-related code, can share the underlying object. `trackerCancelled` is a lifecycle flag used to protect tracker actors. The context owns a fresh `ShardsAffectedByTeamFailure` reference in the UID constructor, which becomes the shared shard/team map used by tracker and queue components.

## Dependencies and Integration Points

The implementation includes `DDSharedContext.h` and `DDRelocationQueue.h`, tying the shared context to the queue type declared in the private header. The header depends on `DataDistributorInterface`, `MoveKeys`, `DDShardTracker`, `ShardsAffectedByTeamFailure`, and `DDTeamCollection`. The context is an integration hub rather than a behavior-heavy component.

## Risks and Edge Cases

The default constructor does not initialize `ddEnabledState`, `ddId`, or `shardsAffectedByTeamFailure` beyond header defaults, so consumers must know whether a default context is only a placeholder. The UID/interface constructors allocate the critical shared objects; code paths that use the default constructor and then call methods like `isDDEnabled()` before initialization would be unsafe. Because `trackerCancelled` is read by actor-safe accessors, its lifetime must outlive actors that reference it.

## Test Signals

There are no local tests in this file. Useful validation is indirect: DD startup tests should confirm context construction wires a shared `ShardsAffectedByTeamFailure`, queue, tracker, and team collections; tracker cancellation tests or simulation failures should exercise `trackerCancelled` lifecycle behavior.
