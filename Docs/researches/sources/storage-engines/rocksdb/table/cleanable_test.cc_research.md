# sources/storage-engines/rocksdb/table/cleanable_test.cc

Purpose: tests cleanup registration/delegation primitives used throughout table/block code to transfer ownership of pinned resources, heap buffers, and cache handles.

Important APIs/types/functions: tests use `Cleanable`, `PinnableSlice`, and `SharedCleanablePtr`. Helper callbacks `Multiplier`, `ReleaseStringHeap`, and `Decrement` make cleanup execution observable. `PinnableSlice4Test` exposes internal cleanup state for validation.

Control flow: `Register` validates no-op cleanup, single cleanup, multiple cleanups, `Reset` executing cleanups, and reuse after reset. `Delegation` checks moving cleanups from one `Cleanable` to another across stack and heap cleanup-node cases. `PinnableSlice` verifies pinning with direct cleanup, cleanup delegation from another cleanable, and self pinning. Shared tests validate copy/move/cleanup transfer behavior for `SharedCleanablePtr`.

State and persistence: all state is in-memory counters and objects; no files are written. The tests rely on destructor timing at scope exit to assert cleanup execution.

Dependencies/integration: includes public RocksDB cleanable/perf/iostats headers and test harness utilities. These primitives are integrated widely with iterators, `BlockContents`, cache entries, and pinnable values.

Risks and test signals: tests guard ordering/lifetime semantics that are easy to regress when changing cleanup storage. They verify moved-from states for analyzer friendliness. They do not test concurrency, but table reader cleanup usage is primarily ownership/lifetime scoped rather than shared mutation.
