<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c

## Purpose
`idmapper_monitoring.c` registers and updates monitoring metrics for idmapping behavior. It tracks user group counts, external resolver latency, cache hit/miss counts, resolution outcomes, cache entry totals, reaped entries, evicted-entry cache duration, and max-groups overflow events.

## Important APIs, types, and functions
- Static metric handle arrays are indexed by `idmapping_op_t`, `idmapping_utility_t`, `idmapping_status_t`, `idmapping_cache_t`, and `idmapping_cache_entity_t`.
- `get_status_name()`, `get_op_name()`, `get_utility_name()`, `get_cache_name()`, and `get_cache_entity_name()` translate enum values into stable metric labels and call `LogFatal()` on unsupported values.
- Registration helpers create one metric per label combination: histograms for user group totals, external latency, and evicted cache duration; counters for cache uses, resolutions, reaped entries, and max-groups exceeded; gauges for total cache entries.
- `idmapper_monitoring__init()` registers every metric and flips `is_inited`.
- Update functions include `idmapper_monitoring__cache_usage()`, `idmapper_monitoring__external_request()`, `idmapper_monitoring__resolution()`, `idmapper_monitoring__user_groups()`, `idmapper_monitoring__evicted_cache_entity()`, `idmapper_monitoring__reaped_cache_entity()`, `idmapper_monitoring__cache_entries_total_set()`, and `idmapper_monitoring__max_groups_exceeded_inc()`.

## Control flow
Startup calls `idmapper_monitoring__init()`, which registers all metric families and all enum-label combinations eagerly. Runtime callers can invoke update APIs before initialization; each public update function checks `is_inited` and returns without touching metric handles if registration has not completed. External latency observations compute a nanosecond difference from start/end times and convert to milliseconds.

## State and persistence
Metric handles and the `is_inited` flag are process-local static state. The monitoring backend owns exported samples after registration and updates. No idmapper data is persisted by this file; it only observes counts, durations, and gauges supplied by callers.

## Dependencies and integration points
The file depends on `idmapper_monitoring.h`, `monitoring.h`, `timespec_diff()`, `NS_PER_MSEC`, and Ganesha logging. Positive and negative cache files call cache-entry, cache-use, reaped, and evicted metrics. Resolver paths call external-request and resolution metrics. Group-list lookup code calls the user-group histogram and max-groups counter.

## Risks
- Every enum value must have a string mapping; adding enum members without updating this file can turn metrics registration or updates into fatal process errors.
- Metric cardinality is fixed by nested loops over enum counts. Incorrect enum count values can register too few or too many handles and later index invalid memory.
- `is_inited` is a plain bool and assumes initialization happens before heavy concurrent updates or that benign lost early samples are acceptable.
- Label values are API-facing monitoring names; changing them can break dashboards and alerts.

## Test signals
- Build tests should catch enum declaration drift with missing switch cases when warnings are strict enough.
- Initialization tests should confirm all metric families register with expected names, units, and labels.
- Runtime tests can call update functions before and after init to confirm pre-init calls are no-ops and post-init calls update the backend.
- Enum-expansion tests should intentionally add a temporary enum value and verify tests fail until a label mapping is provided.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c -->
