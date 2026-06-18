# sources/storage-engines/foundationdb/fdbclient/Schemas.cpp

## Purpose
`Schemas.cpp` defines the static JSON schema/example payloads exposed by `JSONSchemas` in `fdbclient/Schemas.h`. These strings describe the expected shape of FoundationDB status JSON, configuration JSON, latency band configuration, management API errors, health snippets, data-distribution stats, and fault-tolerance status. They are used by CLI tools and simulation workloads as validation contracts rather than runtime parsers.

## Important APIs, types, and functions
The file has no functions. It initializes `const KeyRef` members with raw string literals: `statusSchema`, `clusterConfigurationSchema`, `latencyBandConfigurationSchema`, `dataDistributionStatsSchema`, `logHealthSchema`, `storageHealthSchema`, `aggregateHealthSchema`, `managementApiErrorSchema`, and `faultToleranceStatusSchema`.

The large `statusSchema` includes cluster storage wiggler state, layers, processes and roles, logs, fault tolerance, QoS throttling, lag, lock state, gray failure, latency probes, clients, cache stats, messages, recovery state, workload counters, configuration, consistency scan, data distribution, machines, idempotency ids, version epoch, and client/coordinator status. `clusterConfigurationSchema` focuses on configurable redundancy, regions, storage/log engines, workers, proxies, and backup/range backup worker flags. The fault-tolerance schema is a reduced status view centered on logs, fault tolerance, QoS, recovery, maintenance, data, and client coordinator reachability.

## Control flow
There is no executable control flow beyond static initialization of `KeyRef` constants from string literals using the `_sr` suffix. All validation and interpretation happens in consumers that parse these strings with `json_spirit` or custom schema comparison logic.

## State and persistence behavior
No persistent state is read or written. The constants are compiled into the binary and serve as in-memory references. Any schema drift affects validation behavior in downstream tooling and workloads but not stored data directly.

## Dependencies and integration points
Consumers include `StatusWorkload`, `ChangeConfig`, `Throttling`, `DataDistributionMetrics`, `SpecialKeySpaceCorrectness`, `SpecialKeySpaceRobustness`, `fdbcli/Util.cpp`, `fdbcli/FileConfigureCommand.cpp`, `fdbctl/ControlCommands.cpp`, and `fdbserver/core/LatencyBandConfig.cpp`. `managementApiErrorSchema` is used to validate JSON error messages returned through special-key management APIs. A source comment notes that `mr-status-json-schemas.rst.inc` should be updated alongside the status schema, making documentation synchronization an explicit integration point.

## Risks and edge cases
The schemas use a FoundationDB-specific example/schema convention with markers such as `$enum` and `$map`, so generic JSON Schema tooling will not interpret them as standard JSON Schema. The raw strings must remain syntactically valid JSON despite their size; small formatting mistakes can break consumers at runtime. Because many enum lists mirror live status and configuration strings from other modules, drift can create false test failures or allow incomplete coverage. Some fields are examples rather than exhaustive machine-checkable constraints, so passing validation does not prove all production payload invariants.

## Test signals
Schema consumers are the test signals. `StatusWorkload` parses status schema, `ChangeConfig` and file configuration paths validate configuration and management API error shapes, `Throttling` validates health schemas, `DataDistributionMetrics` validates data distribution stats, and special-key-space workloads validate management errors and fault-tolerance status. A useful guard is to parse every constant as strict JSON and run the existing simulation workloads that compare live JSON to these examples.
