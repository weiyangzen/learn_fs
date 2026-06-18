# Research: sources/storage-engines/pebble/read_state_test.go

- **Purpose:** Benchmarks the synchronization strategy used by `readState` under concurrent load and periodic read-state publication.
- **Important APIs/types/functions:** `BenchmarkReadState` opens an in-memory Pebble DB, then runs sub-benchmarks for update fractions `0`, `0.1`, and `0.5`. Parallel workers randomly either call `d.updateReadStateLocked(nil)` under `d.mu` or call `d.loadReadState()` followed by `s.unref()`.
- **Control flow:** The benchmark creates a DB on `vfs.NewMem`, executes `b.RunParallel`, uses per-worker PCG random generators, and closes the DB after the benchmark cases complete.
- **State and persistence behavior:** Uses an in-memory filesystem, so no durable disk state remains. It repeatedly mutates read-state snapshots and reference counts to measure contention and overhead of the RWMutex plus atomic refcount design.
- **Dependencies:** Depends on `testing`, `math/rand/v2`, `time`, `fmt`, and `vfs.NewMem`. It intentionally reaches package internals (`d.mu`, `updateReadStateLocked`, `loadReadState`, `unref`) because it is in package `pebble`.
- **Integration points:** Serves as performance evidence for the read-state design described in `read_state.go`, especially the comment that RWMutex-based loading benchmarked better than fancier lock-free schemes.
- **Risks:** It is a benchmark, not an assertion-heavy race test. Random update selection may hide some pathological interleavings in short runs, and it does not validate memory reclamation except through absence of crashes under benchmark execution.
- **Test signals:** Run with `go test -bench BenchmarkReadState ./...` or the package-specific equivalent. Useful signals are ns/op and allocation/throughput changes across update fractions; race detector runs can also stress the load/update/unref paths.
