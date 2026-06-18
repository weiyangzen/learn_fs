# Research: sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml

- **Purpose:** Fast simulation test specification for the `ValidateStorage` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 14 lines, 250 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ValidateStorageWorkload, workloads ValidateStorageWorkload, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ValidateStorageWorkload) and schedules each block's workload list (ValidateStorageWorkload:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ValidateStorageWorkload. Top-level keys: configuration, knobs. Configuration/test knobs: config='triple', generateFearless=True, machineCount=18.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ValidateStorageWorkload. Clear-after-test modes: none. Timeouts: none.
