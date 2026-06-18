# Research: sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml

- **Purpose:** Fast simulation test specification for the `MutationLogReaderCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 134 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MutationLogReaderCorrectness, workloads MutationLogReaderCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MutationLogReaderCorrectness) and schedules each block's workload list (MutationLogReaderCorrectness:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MutationLogReaderCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MutationLogReaderCorrectness. Clear-after-test modes: none. Timeouts: none.
