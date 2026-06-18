# Research: sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml

- **Purpose:** Rare simulation test specification for the `RedwoodCorrectnessBTree` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 11 lines, 257 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
