# sources/sync-backup/kopia/internal/fault/fault_set.go

Purpose: manages queues of injectable faults per method and records method call counts for tests.

Important APIs/types/functions: `Method`, `Set`, `NewSet`, `AddFault`, `AddFaults`, `NumCalls`, `VerifyAllFaultsExercised`, and `GetNextFault`. The set stores `map[Method][]*Fault` and `map[Method]int` behind a locker.

Control flow: methods add faults to a FIFO queue. `GetNextFault` increments the call counter, selects the first queued fault, locks both set and fault long enough to decrement `repeatCount` or remove the fault, then releases locks before sleeping and invoking callbacks. If an error callback exists, it returns `(true, err)`; otherwise it returns `(false, nil)` even if a before-callback or sleep ran.

State/persistence behavior: all state is memory-local. Queued faults are consumed over time, and `VerifyAllFaultsExercised` fails a test if any configured fault remains.

Dependencies/integration: depends on `testing` for verification, `context` plus repository logging for debug messages, and `Fault` internals from `fault.go`. Integrates with test-only storage or service wrappers that call `GetNextFault` before real methods.

Risks/test signals: callbacks run without locks, which is good for deadlock avoidance but means callbacks observe external state only. `time.Sleep` ignores context cancellation. There are no direct tests in this subset, so coverage likely comes from packages that use fault injection.
