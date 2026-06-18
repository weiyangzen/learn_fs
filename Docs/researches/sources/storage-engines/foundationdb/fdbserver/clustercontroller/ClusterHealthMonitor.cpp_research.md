# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.cpp

## Purpose

`ClusterHealthMonitor.cpp` implements production event collection and the periodic aggregate cluster-health metric loop.

## Important APIs, Types, and Functions

- `latestEventOnWorker()` fetches a latest worker event with a 2-second timeout.
- `latestEventOnInterfaces()` fetches interface-scoped events such as `<interface id>/<eventName>` and records failures per address.
- `levelToInt()` and `levelToStr()` define numeric and string representations for health levels.
- `WorkerEventProvider` setters snapshot workers, recovery state, role interfaces, storage servers, TLogs, and one-replica criticality.
- Provider methods fetch all-worker, ratekeeper, data-distributor, storage-server, and TLog events.
- `Monitor::run()` polls factors, chooses the lowest-valued level as aggregate, and logs `ClusterHealthMetric`.
- `Monitor::create()` constructs the default factor list from server knobs.

## Control Flow

The monitor returns immediately when disabled. Otherwise it delays by `CLUSTER_HEALTH_METRIC_POLL_INTERVAL`, launches all factor futures, waits for them, emits per-factor details, and records the aggregate value and limiting factor. Event-log RPC errors are represented as empty fields plus failed addresses rather than failing the whole poll.

## State and Persistence Behavior

Provider and monitor state are in-memory snapshots and references. Output is trace logging only.

## Dependencies and Integration Points

The file integrates with Flow actors, `WorkerEvents`, `EventLogRequest`, worker/storage/TLog interfaces, server knobs, `fmt`, `TraceEvent`, and factor implementations. `ClusterControllerData` owns and refreshes the provider.

## Risks

Timeouts can turn slow workers into missing metrics. Address-to-worker matching can miss role metrics if snapshots are stale. Any new `Level` must be added consistently to both mapping functions and aggregate ordering.

## Test Signals

The main operational signal is the `ClusterHealthMetric` trace with factor details, aggregate string/value, and limiting factor. Unit tests primarily validate the factors rather than the production polling loop.
