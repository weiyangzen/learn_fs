# sources/storage-engines/foundationdb/fdbserver/core/ServerKnobs.cpp

## sources/storage-engines/foundationdb/fdbserver/core/ServerKnobs.cpp

Purpose: defines global server knob storage, parsing, mutation helpers, and the authoritative initialization table for `ServerKnobs`. This file is the runtime configuration surface for transaction logs, data distribution, storage engines, recovery, ratekeeper, worker health, backup, bulk load/dump, simulation fault injection, and many timing/resource limits.

Important APIs: `ServerKnobs::ServerKnobs`, `ServerKnobs::initialize`, `resetServerKnobs`, `initializeServerKnobs`, `tryParseServerKnobValue`, `parseServerKnobValue`, `trySetServerKnob`, `setServerKnob`, and `setupServerKnobs`. It also owns the global `SERVER_KNOBS` pointer plus bootstrap/global instances of Flow, client, and server knobs.

Control flow and state: process startup begins with bootstrap knobs, then `resetServerKnobs` points `FLOW_KNOBS`, `CLIENT_KNOBS`, and `SERVER_KNOBS` at global instances and reinitializes all three. `initializeServerKnobs` mutates already-selected global instances. Parsing searches Flow, client, then server knob registries. Setting attempts all three mutable knob objects and reports invalid name/value warnings through stderr and trace events. `ServerKnobs::initialize` uses `INIT_KNOB` for hundreds of values, with many derived from earlier knobs and with simulation/buggify branches that deliberately shrink timeouts, limits, shard sizes, or queue sizes.

State and persistence behavior: knobs are in-memory process-global configuration, but many values affect persistent protocols and on-disk interpretation. Examples include byte sampling constants that cannot change after database creation, DBCoreState serialization gates, RocksDB and sharded RocksDB layout/checkpoint behavior, transaction log recovery limits, and data distribution priorities.

Dependencies and integration: depends on `fdbserver/core/Knobs.h`, client knobs, Flow randomization, trace events, and simulation helpers. Nearly every server component reads `SERVER_KNOBS`; this file is therefore a cross-cutting integration point.

Risks and tests: ordering matters because later knobs depend on earlier values. Simulation-only randomization should not leak into production defaults. Changes can destabilize recovery, storage queue throttling, shard splitting/merging, RocksDB performance, or compatibility. Test signals include simulation suites with buggify, restart/downgrade tests for persistent knobs, storage metric split tests, data distribution tests, and targeted workload tests for any changed knob family.
