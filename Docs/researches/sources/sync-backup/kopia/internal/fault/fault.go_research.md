# sources/sync-backup/kopia/internal/fault/fault.go

Purpose: defines a configurable single fault used by test doubles and storage wrappers to inject delays, callbacks, and replacement errors.

Important APIs/types/functions: `Fault`, `New`, `ErrorInstead`, `ErrorCallbackInstead`, `Before`, `Repeat`, and `SleepFor`. Internal fields include `repeatCount`, `sleep`, `callback`, and `errCallback`, all protected by a mutex.

Control flow: builder-style methods lock the fault, mutate one behavior field, unlock, and return the same receiver for chaining. `ErrorInstead` wraps a fixed error in a callback; `ErrorCallbackInstead` stores dynamic error computation; `Before` stores a side-effect callback; `Repeat` controls how many extra invocations the fault remains queued; `SleepFor` sets a delay.

State/persistence behavior: state is in-memory and mutable. The fault itself does not execute; `fault.Set` owns call counting, queue consumption, sleeps, and callback invocation.

Dependencies/integration: uses only `sync` and `time`, but is tightly coupled to `fault_set.go` which reads these fields under locks. It is typically used by tests that need deterministic failure injection in repository or blob operations.

Risks/test signals: multiple builder calls overwrite prior callbacks or errors. The repeat counter semantics are implemented externally, so callers must understand that `Repeat(n)` means the fault is observed while the set decrements the count before removing it.
