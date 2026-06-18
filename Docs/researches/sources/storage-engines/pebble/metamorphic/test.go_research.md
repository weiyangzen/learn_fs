<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/test.go -->
## sources/storage-engines/pebble/metamorphic/test.go

Purpose: defines the runtime harness that executes parsed/generated metamorphic operations against one or more Pebble DB instances while recording deterministic history and handling test-specific filesystem, remote-storage, retry, and synchronization behavior.

Important APIs and types: `New` constructs a single-instance `Test`. `Test` stores operations, synchronization data, options, DB handles, object slots for batches/iterators/snapshots/external objects, and remote external storage. Key methods include `init`, `finalizeOptions`, `restartDB`, `Step`, `runOp`, object slot setters/getters, and `computeSynchronizationPoints`.

Control flow: `init` clones and finalizes options, wraps listeners to fail on background errors, opens custom options, opens each DB, initializes shared/external storage, and creates temporary directories. `Step` runs one operation through `runOp`; `runOp` applies timeout multipliers for slow operations and optional treesteps recording before invoking `op.run`. `computeSynchronizationPoints` computes wait dependencies from each op's receiver and synchronization objects for parallel execution.

State and persistence: the harness owns live DB, batch, iterator, snapshot, and external object state. In strict FS mode it syncs directories and supports crash-clone restarts on in-memory FS. On serious background errors it clones in-memory data to disk for debugging and exits. Shared/external storage is represented by local directories and `remote.Storage` factories.

Dependencies and integration: integrates with Pebble `Options`, event listeners, `objstorageprovider`, `remote`, `vfs`, `errorfs`, operation implementations, history logging, and custom option hooks. `retryableIter` is installed by `setIter`.

Risks and edge cases: background errors call `os.Exit(1)`, which is appropriate for metamorphic binaries but hostile to library-style callers. Multi-DB restart is disabled because DBs share FS. Object slots are assertion-heavy; stale IDs panic. Synchronization depends on every op reporting correct `receiver` and `syncObjs`.

Test signals: broad metamorphic integration tests exercise this harness; listed parser tests verify operation-derived fields used by synchronization and execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/test.go -->
