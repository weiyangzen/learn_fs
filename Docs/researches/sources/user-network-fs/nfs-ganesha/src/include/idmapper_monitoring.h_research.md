# sources/user-network-fs/nfs-ganesha/src/include/idmapper_monitoring.h

## Purpose

`idmapper_monitoring.h` declares the metrics surface for ID mapping. It gives idmapper implementations stable enum label sets for external resolver latency, operation success/failure, cache usage, group-count observations, and cache eviction/reap accounting.

## Important APIs, Types, and Functions

The enums define metric dimensions: `idmapping_utility_t` distinguishes pwutils, nfsidmap, and winbind; `idmapping_op_t` names UID/user/group/principal/SID resolution flows; `idmapping_cache_t` names positive and negative cache lookup classes; `idmapping_cache_entity_t` aggregates entity types; and `idmapping_status_t` separates success and failure. Update functions include `idmapper_monitoring__external_request`, `__cache_usage`, `__resolution`, `__user_groups`, `__evicted_cache_entity`, `__reaped_cache_entity`, and `__cache_entries_total_set`.

## Control Flow

The monitoring package is registered once through `idmapper_monitoring__init`. Resolver code records elapsed times with start/end `timespec` values, cache lookup code records hit/miss events, and cache maintenance records evicted or reaped entity classes.

## State and Persistence Behavior

No cache state is owned by this header. Implementations likely keep metric handles registered with the dynamic metrics subsystem; exported values are process-lifetime counters, gauges, or histograms.

## Dependencies and Integration Points

It depends on `common_utils.h` for elapsed-time types and on the ID mapper's resolver/cache code. Metrics consumers are monitoring exporters and operational dashboards that need to diagnose directory-service latency, cache effectiveness, and max-group-limit behavior.

## Risks and Test Signals

The enum order is a metrics label ABI; inserting values in the middle can break dashboards. Callers must not pass out-of-range enum values and should consistently mark success/failure. Tests should initialize metrics, emit each enum path, verify cache hit/miss counters, confirm latency buckets use nonnegative durations, and validate max-groups and cache-entry gauges after cache mutation.
