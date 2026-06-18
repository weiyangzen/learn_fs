# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/Knobs.h

## Purpose
`Knobs.h` declares `ServerKnobs`, the server-side runtime tuning surface for FoundationDB. It centralizes hundreds of typed knobs that shape version advancement, transaction logs, data distribution, storage engines, recovery, ratekeeper limits, worker health, coordination, tracing, encryption, Redwood/RocksDB behavior, simulation probabilities, and feature flags.

## Important APIs, Types, And Functions
The key type is `ServerKnobs : KnobsImpl<ServerKnobs>`, constructed and initialized with `Randomize`, `ClientKnobs*`, and `IsSimulated`. Public lifecycle helpers are `resetServerKnobs`, `initializeServerKnobs`, `setupServerKnobs`, `tryParseServerKnobValue`, `parseServerKnobValue`, `trySetServerKnob`, and `setServerKnob`. `SERVER_KNOBS` is the global singleton pointer and `getServerKnobs()` returns a reference.

## Control Flow
This header is declarative; initialization and parsing are implemented elsewhere. Runtime code reads fields directly from `SERVER_KNOBS`, while setup code parses knob overrides and simulation randomization before roles start.

## State And Persistence Behavior
Knobs are process memory state, not durable database state. They indirectly affect persistent behavior by changing log retention, MVCC windows, storage engine options, checkpoint settings, compaction, movement throttles, and recovery timing. Unsafe or randomized knobs can change simulation determinism and operational safety.

## Dependencies And Integration Points
It depends on `KnobValue`, `flow/Knobs.h`, Swift support, RPC locality, and client knobs. Nearly every server subsystem integrates through this file: TLogs, commit proxies, resolvers, DD, ratekeeper, storage servers, cluster controller, workers, coordination, and storage engines.

## Risks And Edge Cases
The risk is configuration coupling: changing a knob type, name, default, or unit can silently alter consensus, recovery, rate limiting, or storage behavior. Several comments mark experimental or dangerous settings, such as storage-server reboot on I/O timeout, RocksDB nondeterminism, sharded RocksDB experiments, and physical-shard movement.

## Test Signals
Tests typically observe this file indirectly through simulation suites and role-specific tests. Good signals are explicit knob override parsing, deterministic randomized values in simulation, feature-gated behavior, storage engine option propagation, and workload/recovery tests passing under randomized knobs.
