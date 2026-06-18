# sources/storage-engines/foundationdb/documentation/sphinx/source/mr-status-json-schemas.rst.inc

## Purpose
Documents the shape of FoundationDB machine-readable status JSON using a large `javascript` code block. It is schema-like reference material for operators and tooling authors.

## Important APIs, Types, and Functions
Documents `cluster` and `client` status structures: storage wiggler, consistency scan, layers, processes/roles, RocksDB metrics, latency statistics/bands, logs, fault tolerance, QoS, lag, clients, messages, recovery state, workload, configuration, data distribution, machines, idempotency ids, version epoch, coordinators, database status, and cluster file state. Enum placeholders describe process classes, roles, storage engines, recovery states, redundancy modes, and status messages.

## Control Flow
Sphinx renders the block as documentation. It is not strict JSON because it includes comments and placeholders like `$map_key` and `$enum`.

## State and Persistence Behavior
Captures expected status fields at documentation time, including persistent configuration and ephemeral counters/health data. Many fields are optional or version/role/configuration dependent.

## Dependencies and Integration Points
Integrates with the status documentation page and the implementation that emits `status json`. Downstream integration includes dashboards, parsers, and operational runbooks.

## Risks
High documentation drift risk because the example is hand-maintained and large. Tool authors may treat it as parseable JSON. Optional field behavior is mostly conveyed by comments.

## Test Signals
Build docs and compare documented field names/enums against representative `status json` fixtures from simulation and real clusters, especially after status or configuration changes.
