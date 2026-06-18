# sources/storage-engines/foundationdb/fdbserver/sequencer/MasterData.h

Purpose: declares internal state for the master/sequencer actor that assigns commit versions and publishes live committed versions.

Important APIs and types: `CounterValue` wraps shared `Counter` ownership and exposes increment/add/clear. `MasterData` stores DB id, epoch/recovery versions, live committed version, lock/metadata state, min known committed version, coordinators, current assigned version, reference version, per-proxy duplicate-suppression maps, master interface, `ResolutionBalancer`, forced recovery flag, storage-server version vector, primary locality, counters, latency samples, actor stream, logger, and balancer actor.

Control flow, state, and persistence: all members are in-memory for a master lifetime. Durable epoch and recovery state are supplied through `UpdateRecoveryDataRequest` and `ServerDBInfo`; this struct does not write storage directly.

Dependencies and integration: depends on master, coordination, server DB info, version-vector, Trace/counter, and resolution balancing types. `masterserver.cpp` constructs and mutates it.

Risks and test signals: risks are lifetime-sensitive references, duplicate reply retention, invalid version initialization, and version-vector locality handling. Tests should cover constructor initialization, counters, forced recovery locality validation, and version vector sample creation when enabled.
