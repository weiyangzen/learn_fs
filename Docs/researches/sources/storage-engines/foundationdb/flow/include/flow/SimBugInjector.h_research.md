<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SimBugInjector.h -->
# sources/storage-engines/foundationdb/flow/include/flow/SimBugInjector.h

Purpose: This header defines a controlled bug-injection framework for simulation and negative tests. Unlike buggify, it injects intentional bugs so tests can prove they catch expected failures.

Important APIs and types: `ISimBug` represents a bug instance with `name`, `hit`, `numHits`, and virtual `onHit`. `IBugIdentifier` creates bug instances. `SimBugInjector` exposes `enable`, `disable`, `reset`, `isEnabled`, templated `get<T>`, and templated `enable<T>` backed by `getImpl` and `enableImpl`.

Control flow: Code defines an `IBugIdentifier` for each bug. When global injection is enabled, callers enable a specific bug id and later fetch it. Calling `ISimBug::hit()` records a hit and invokes overridable `onHit`. `disable` preserves state for later re-enable; `reset` clears state.

State and persistence behavior: State is singleton-backed, process-local simulation state. Bug instances are held as `std::shared_ptr<ISimBug>` to support polymorphism and weak references. No state is persisted.

Dependencies and integration points: It depends on standard memory/string headers and Flow's simulated network precondition in implementation. It is used by simulation tests and targeted negative-test hooks where actual bugs must be injected deterministically.

Risks: `enable()` has a precondition that the network is simulated; enabling in production would be dangerous. Templated `get<T>` uses `dynamic_pointer_cast`, so incorrect expected types produce null. Injection hooks can make tests non-representative if left enabled or not reset.

Test signals: Tests should cover global enable/disable/reset, per-identifier instance creation and reuse, hit counting, subclass `onHit`, disabled lookup behavior with `getDisabled`, and simulation-only precondition enforcement.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SimBugInjector.h -->
