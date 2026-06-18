# Research: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml

- **Purpose:** Negative simulation test specification for `ResolverIgnoreWrites`. It intentionally exercises error or fault behavior where the expected signal is not normal success-path workload completion.
- **Source facts:** 6 lines, 120 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ResolverIgnoreReads, workloads ResolverBug, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ResolverIgnoreReads) and schedules each block's workload list (ResolverIgnoreReads:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ResolverBug. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `negative` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml` through the Python TestRunner/CTest path.
- **Risks:** Negative tests rely on expected failure/ignore behavior, so a plain non-zero exit is not always enough context without matching trace assertions.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ResolverBug. Clear-after-test modes: none. Timeouts: none.
