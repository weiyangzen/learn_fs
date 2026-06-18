
# sources/user-network-fs/nfs-ganesha/src/SAL/sal_metrics.c

## Purpose

`sal_metrics.c` registers and updates monitoring metrics for selected SAL client, lock, session, transport, and lease events. It is a thin instrumentation layer around the repository's monitoring API.

## Important APIs, types, and functions

- Metric handles include gauges for confirmed clients and lock counts, counters for lease expiry, client state protection, denied xprt associations, and xprt custom-data status, plus histograms for session connections and sessions per xprt.
- `sal_metrics__init()` registers every metric and must run before update functions.
- Update functions include `sal_metrics__confirmed_clients()`, `sal_metrics__lease_expire()`, `sal_metrics__client_state_protection()`, `sal_metrics__locks_inc()`, `sal_metrics__locks_dec()`, `sal_metrics__session_connections()`, `sal_metrics__xprt_association_denied()`, `sal_metrics__xprt_custom_data_status()`, and `sal_metrics__xprt_sessions()`.
- Label conversion helpers map `xprt_custom_data_status_t` and `state_protect_how4` enums to stable label strings and `LogFatal()` on unsupported values.

## Control flow

Initialization registers groups of metrics: client metrics first, then session connection histogram, denied association counter, xprt status counters, and xprt session histogram. Counter metrics with enum labels are registered once per enum value. Runtime update functions directly call `monitoring__*` primitives with the already stored handles.

## State and persistence behavior

All state is in process-local metric handles and static bucket arrays. The file does not persist data itself; persistence/export is delegated to the monitoring subsystem. Gauges track current values where callers provide increments/decrements or absolute count; counters are monotonic; histograms observe samples.

## Dependencies and integration points

The file depends on `sal_metrics.h`, common utilities for `ARRAY_SIZE`, `nfs_convert.h` for enum definitions, and the monitoring API macros/types. It is called from client/session/xprt/lock lifecycle paths elsewhere in SAL and NFSv4.

## Risks and edge cases

- Update functions assume `sal_metrics__init()` ran and handles are valid.
- Enum conversion helpers fail fatally for out-of-range values, which catches programming errors but can make unexpected input process-fatal.
- `sal_metrics__client_state_protection()` and xprt status updates index arrays directly by enum value; enum count/order changes must update counts and conversion logic together.
- Lock gauges rely on balanced inc/dec calls in other modules.

## Test signals

Tests should validate metric registration names, labels, bucket boundaries, enum label coverage, and update calls. Integration tests can assert lock gauge balance, confirmed-client gauge updates, session/xprt histogram observations, and fatal behavior for invalid enum values in debug/fault-injection builds.
