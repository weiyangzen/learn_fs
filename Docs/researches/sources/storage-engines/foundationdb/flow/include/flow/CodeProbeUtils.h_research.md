# sources/storage-engines/foundationdb/flow/include/flow/CodeProbeUtils.h

Purpose: declares helper utilities for reporting code probes that were expected but not hit.

Important APIs/types/functions: `probe::traceMissedProbes(Optional<ExecutionContext> context)`.

Control flow: implementation elsewhere likely iterates registered probes and emits trace events for misses, optionally filtered by execution context.

State/persistence: no state in the header; depends on global probe registry from `CodeProbe.h`.

Dependencies/integration: includes `flow/CodeProbe.h` and `flow/Arena.h` for `Optional`.

Risks: behavior is only declared here; correctness depends on implementation matching annotation/context semantics in `CodeProbe.h`.

Test signals: simulation or net2 coverage runs that call `traceMissedProbes` and verify missed probe trace output.
