# sources/storage-engines/foundationdb/fdbserver/worker/RoleLineage.h

## Purpose
`RoleLineage.h` defines actor-lineage metadata for FoundationDB worker roles, allowing lineage profiling to record and collect a process role abbreviation.

## Important APIs, Types, And Functions
`RoleLineage` derives from `LineageProperties<RoleLineage>`, declares static `name`, and stores `ProcessClass::ClusterRole role`, defaulting to `NoRole`. Its `isSet` helper treats any role other than `NoRole` as present. `RoleLineageCollector` derives from `IALPCollector<RoleLineage>` and returns the role abbreviation from `Role::get(...)` when present.

## Control Flow
Collectors call `collect(ActorLineage*)`, retrieve the nearest lineage role property, and return either an `std::any` containing the abbreviation or an empty optional.

## State And Persistence Behavior
State is in-memory actor-lineage metadata only. It is intended for profiling/diagnostic collection, not persistence.

## Dependencies And Integration Points
The header integrates `ActorLineageProfiler` with worker role definitions from `WorkerInterface.actor.h`. It maps internal `ProcessClass::ClusterRole` values to user-facing `Role` abbreviations.

## Risks And Test Signals
The collector assumes `Role::get` supports every collected cluster role. Roles left as `NoRole` are intentionally omitted. Coverage is likely through actor-lineage profiling rather than direct unit tests.
