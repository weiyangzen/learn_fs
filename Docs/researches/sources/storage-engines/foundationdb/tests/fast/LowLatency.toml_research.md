# Research: sources/storage-engines/foundationdb/tests/fast/LowLatency.toml

- **Purpose:** Fast simulation test specification for the `LowLatency` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 35 lines, 1067 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Cycle, LowLatency, Attrition, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, LowLatency, Attrition. Top-level keys: configuration, knobs. Configuration/test knobs: buggify=False, minimumReplication=2, Clogged/Cycle.testDuration=30.0, Clogged/Cycle.transactionsPerSecond=1000.0, Clogged/LowLatency.testDuration=30.0, Clogged/Attrition.testDuration=30.0, Clogged/Attrition.machinesToKill=1, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/LowLatency.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, LowLatency, Attrition. Clear-after-test modes: none. Timeouts: none.
