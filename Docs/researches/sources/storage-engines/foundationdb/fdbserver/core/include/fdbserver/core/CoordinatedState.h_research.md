# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinatedState.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/CoordinatedState.h

Purpose: declares abstractions for reading, exclusively updating, and moving the cluster coordinated state stored through server coordinators.

Important APIs/types: `CoordinatedState` with `read`, `onConflict`, `setExclusive`, and `getConflict`; `MovableCoordinatedState` with the same read/conflict/set flow plus `move`.

Control flow and state: callers must call `read()` before the single allowed `setExclusive()`. `onConflict()` is also single-use after read and completes when a future exclusive update would fail. `setExclusive()` attempts compare-and-set semantics against the value returned by read, but comments warn that concurrent reads/sets can make conflict outcomes ambiguous. `MovableCoordinatedState::move` runs only after successful `setExclusive` and transfers coordinated state to new uninitialized coordinators until a leader from the new coordinators should continue work.

State and persistence behavior: implementations hidden behind `PImpl` persist through coordination backends. The API is a concurrency-sensitive wrapper over cluster state history.

Dependencies and integration: depends on FDB values, `PImpl`, `ServerCoordinators`, and cluster connection strings. Master recovery and coordinator migration use these abstractions.

Risks and tests: lifetime comments require all outstanding operations to be cancelled before destruction. Single-use method ordering and concurrent calls are easy to misuse. Tests should cover successful exclusive set, conflict, onConflict behavior, move after set, cancellation/destruction, and ambiguous concurrent interleavings.
