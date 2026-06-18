# Research: sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml

- **Purpose:** Rare simulation test specification for the `CycleWithKills` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 15 lines, 350 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CycleTestWithKills, workloads Cycle, Attrition, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CycleTestWithKills) and schedules each block's workload list (CycleTestWithKills:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, Attrition. Top-level keys: testPriority. Configuration/test knobs: CycleTestWithKills/Cycle.testDuration=30.0, CycleTestWithKills/Cycle.transactionsPerSecond=2500.0, CycleTestWithKills/Attrition.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, Attrition. Clear-after-test modes: none. Timeouts: none.
