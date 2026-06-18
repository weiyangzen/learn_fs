# sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageCorruptionBug.h

## Purpose
`StorageCorruptionBug.h` declares a simulation-only bug descriptor used to inject storage mutation loss in the storage server. It gives FoundationDB simulation workloads a typed handle for enabling, configuring, and counting deliberate corruption events through `SimBugInjector`.

The file contains only the bug payload and its identifier factory. The actual fault behavior is implemented in `StorageServerDisk::writeMutationsBuggy()` in `storageserver.actor.cpp`, and the workload that enables the bug lives in `fdbserver/workloads/StorageCorruption.cpp`.

## Important APIs, Types, and Functions
- `class StorageCorruptionBug : public ISimBug` is the bug payload. It inherits the shared simulation bug accounting behavior, including hit counting through `ISimBug::hit()`.
- `double corruptionProbability = 0.001` controls the per-mutation probability that a mutation is skipped when the bug is active. The default is one corruption attempt per thousand mutation positions.
- `class StorageCorruptionBugID : public IBugIdentifier` identifies this bug type to the injection registry.
- `std::shared_ptr<ISimBug> StorageCorruptionBugID::create() const override` returns a new `StorageCorruptionBug` instance for the injector.

## Control Flow
The header itself has no runtime control flow beyond the inline factory. In simulation, `StorageCorruptionWorkload` creates a `SimBugInjector`, enables a `StorageCorruptionBug` by passing `StorageCorruptionBugID`, optionally overrides `corruptionProbability` from workload options, and enables the injector for a configured duration.

On the storage server side, `StorageServerDisk::writeMutationsBuggy()` asks `SimBugInjector().get<StorageCorruptionBug>(StorageCorruptionBugID())` for the active bug. If none is present, it delegates to the normal `writeMutations()` path. If a bug is active, it scans the mutation vector, writes the contiguous slice before each selected mutation, calls `bug->hit()`, skips that selected mutation, and continues. `makeVersionMutationsDurable()` calls `writeMutationsBuggy()` when applying mutation-log entries to the key-value store, so the fault drops durable storage writes rather than client request handling directly.

## State and Persistence Behavior
`StorageCorruptionBug` stores only the mutable probability in memory. It does not persist to disk and is active only while the simulation injector is enabled. The injected effect, however, deliberately changes storage persistence behavior: selected mutations are not written to the backing `IKeyValueStore` during durable version application. This creates storage contents that diverge from the expected mutation stream, allowing consistency-check and recovery paths to observe corruption.

The workload sets `corruptionProbability` back to `0.0` after its delay, logs the number of hits, disables the injector, and re-enables data distribution. The skipped mutations remain as durable corruption in the simulated storage engine unless later overwritten or cleared by normal cluster activity.

## Dependencies and Integration Points
The header depends on `flow/SimBugInjector.h`, specifically `ISimBug`, `IBugIdentifier`, and the shared injector API. It is included by `storageserver.actor.cpp` and by the `StorageCorruption` simulation workload.

The main integration points are simulation policy and consistency checking. `StorageCorruptionWorkload` disables all other failure-injection workloads, disables data distribution with `setDDMode(cx, 0)`, enables this bug, waits, stops corruption, installs an uncancellable listener for `ConsistencyCheckFailure`, then turns data distribution back on. A severity-error consistency-check failure is treated as negative-test success by tracing `NegativeTestSuccess`.

## Risks and Edge Cases
This type must remain simulation-scoped. Accidentally enabling the injector in non-simulation or production-like tests would intentionally corrupt durable storage data. The current use depends on `SimBugInjector` availability and workload control rather than compile-time exclusion in the header itself.

The probability is public and unconstrained. Values below zero behave like zero in the comparison against `random01()`, values above one drop every mutation encountered, and very high probabilities can make a storage server unusable before the intended consistency-check signal occurs. Because `writeMutationsBuggy()` drops whole mutation entries, not bytes, the impact depends on workload mutation shape: dropping a clear range is much larger than dropping a small set.

The header's identifier creates a fresh bug instance; callers must use the same identifier type when enabling and retrieving the bug or the storage-server path will not see the workload's configuration. The `writeMutationsBuggy()` loop has a critical normal-path behavior: if `get()` returns no bug, it calls `writeMutations()` but does not explicitly return before continuing to dereference `bug`. That implementation detail should be checked carefully in context before changes, because the intended contract is clearly "no bug means normal writes." The test workload exercises the active-bug path, so a separate no-bug coverage signal is useful.

## Test Signals
The direct workload signal is `fdbserver/workloads/StorageCorruption.cpp`. It logs `CorruptionInjections` with `NumCorruptions`, observes `ConsistencyCheckFailure`, and emits `NegativeTestSuccess` when the expected severe consistency-check error is detected. Broader signals include simulation tests using the `StorageCorruption` workload, storage consistency-check traces, and successful cleanup after data distribution is re-enabled. Compile coverage verifies the `IBugIdentifier` factory and typed `SimBugInjector::enable/get` calls remain compatible.
