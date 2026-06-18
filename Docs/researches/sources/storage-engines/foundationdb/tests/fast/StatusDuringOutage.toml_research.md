# Research: sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml

- **Purpose:** Fast simulation test specification for the `StatusDuringOutage` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 26 lines, 662 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StatusDuringOutage, workloads Status, Attrition, RandomClogging, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StatusDuringOutage) and schedules each block's workload list (StatusDuringOutage:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Status, Attrition, RandomClogging. Top-level keys: none. Configuration/test knobs: StatusDuringOutage/Status.testDuration=60.0, StatusDuringOutage/Attrition.testDuration=60.0, StatusDuringOutage/Attrition.machinesToKill=10, StatusDuringOutage/Attrition.machinesToLeave=1, StatusDuringOutage/RandomClogging.testDuration=60.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Status, Attrition, RandomClogging. Clear-after-test modes: none. Timeouts: none.
