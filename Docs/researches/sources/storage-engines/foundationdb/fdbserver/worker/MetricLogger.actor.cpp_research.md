# sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.cpp

## Purpose
`MetricLogger.actor.cpp` implements two metric pipelines. `runMetrics(Future<Database>, Key)` persists TDMetric data and metric registration/rules into a FoundationDB database prefix. The parameterless `runMetrics()` periodically emits process metrics over UDP using `UDPMetricClient`, with a simulation UDP server for validation.

## Important APIs, Types, And Functions
`MetricsRule` represents a DB-backed rule with substring pattern fields for name, type, address, and ID plus enable/min-level settings. `MetricsConfig` builds system-key subspaces/maps for rules, enum maps, and change keys. `metricRuleUpdater` reads DB rules and applies them to registered TD metrics. `MetricDB` implements `IMetricDB::getLastBlock` for metric callbacks. `dumpMetrics` flushes metric batches, runs callbacks, and writes inserts/appends/updates. `updateMetricRegistration` registers metric field keys and enum keys. `runMetrics(fcx, prefix)` orchestrates DB-backed TD metric logging. `startMetricsSimulationServer` receives and validates UDP metrics in simulation. `runMetrics()` emits UDP metrics at `FLOW_KNOBS->METRICS_EMISSION_INTERVAL`. The `TraceEvents` unit test writes synthetic trace events and TDMetric handles to an external metrics database.

## Control Flow
The DB-backed path waits until `TDMetricCollection` exists and initializes, constructs config, waits for the database future, then races rule update, dump, and registration actors. Any non-cancellation error disables all metrics and rethrows.

`metricRuleUpdater` repeatedly reads all rules under system-key access, disables every metric, applies rules in reverse order so later rules win, watches the rule-change key, commits, and waits for either rule changes or new metrics. `dumpMetrics` flushes each metric into a `MetricBatch`, invokes callbacks with retry-on-error, commits batch mutations, and waits based on roll times or metric-enabled triggers. `updateMetricRegistration` writes missing field and enum keys, then waits for registration changes or new metrics.

The UDP path returns immediately if metric model is `NONE`, optionally starts a simulated UDP server, then loops: fetch global `MetricCollection`, call `UDPMetricClient::send`, and sleep for the emission interval.

## State And Persistence Behavior
DB-backed metrics persist under the caller-supplied prefix using key-backed rule, address, name/type, field, enum, and block keys. Transactions use `ACCESS_SYSTEM_KEYS`. Runtime state lives in `TDMetricCollection`, `MetricCollection`, registered flags, roll-time queues, and metric enabled/config flags. UDP metrics are not durable.

## Dependencies And Integration Points
The file integrates with FoundationDB database APIs, ReadYourWrites transactions, KeyBackedTypes, TDMetric and OTEL metrics, Flow actor compiler, UDP sockets, Msgpack, knobs, unit tests, and the `UDPMetricClient`. External environment variables `METRICS_CONNFILE` and `METRICS_PREFIX` drive the trace-event metrics test.

## Risks And Test Signals
Rule matching is simple substring matching and full rescans may become expensive with many metrics/rules. Transaction retries in dump callbacks must be idempotent. The simulation server switch lacks `break` statements, so `STATSD` falls through to the OTLP port assignment; that is a potential correctness issue for StatsD validation. The `/fdbserver/metrics/TraceEvents` test is manual/environment-driven and writes a large synthetic stream for plotting/inspection.
