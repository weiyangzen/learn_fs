# sources/storage-engines/foundationdb/fdbserver/workloads/ResolverBug.cpp

## Purpose
`ResolverBugWorkload` is a negative-test harness for simulated resolver bugs. It enables a `ResolverBug` injector with configurable probabilities, repeatedly runs the existing `Cycle` workload while toggling the injector, and treats any `TestFailure` error trace as expected evidence that the injected resolver bug was detected.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `ResolverBug`. Key members are `ResolverBug resolverBug`, `cycleOptions`, `createCycle`, `driveWorkload`, `_start`, `waitForPhase`, `waitForPhaseDone`, and `onBug`. It uses `SimBugInjector`, `ResolverBugID`, `ProcessEvents::Event`, and `BaseTraceEvent` severity inspection.

## Control Flow
The constructor strips options with a `cycle_` prefix into `cycleOptions`, installs the bug injector on client 0, and sizes `bug->cycleState` to the client count. Client 0 runs `driveWorkload`, which cycles phases: setup with injector disabled, start with injector enabled, and check with injector disabled. Every client runs `_start`, which creates a fresh `Cycle` workload for each phase and records its client phase in shared bug state. `start` races phase execution with `onBug`, which logs `NegativeTestSuccess` once a severe `TestFailure` trace is observed.

## State And Persistence Behavior
The durable database state is whatever the nested `Cycle` workload writes. Resolver bug configuration and phase state live in the process-local simulation bug injector. `bugFound` is a shared in-memory flag set by trace observation rather than by reading database state.

## Dependencies And Integration Points
It depends on `flow/ProcessEvents`, `fdbserver/resolver/ResolverBug.h`, `ServerDBInfo`, and the workload factory interface. It can disable all failure injection workloads by default so the observed failure is attributable to resolver bug injection rather than unrelated chaos.

## Risks And Edge Cases
The workload is intentionally successful only when a failure is detected. If no `TestFailure` is emitted, it runs indefinitely through `waitForAll`. It relies on trace-event process hooks and global `g_traceProcessEvents`, so unrelated code changing trace names, severities, or process event delivery can break the negative-test signal.

## Test Signals
The positive signal is `NegativeTestSuccess`. Severe `TraceEvent::TestFailure` events set `bug->bugFound`. `check` always returns true because success is encoded in the early completion path, not final database validation.
