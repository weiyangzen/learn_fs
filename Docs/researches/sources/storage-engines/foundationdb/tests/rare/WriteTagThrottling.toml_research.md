# Research: sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml

- **Purpose:** Rare simulation test specification for the `WriteTagThrottling` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 39 lines, 815 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles withoutWriteThrottling, withWriteThrottling, workloads WriteTagThrottling(2), HealthMetricsApi(2), top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (withoutWriteThrottling, withWriteThrottling) and schedules each block's workload list (withoutWriteThrottling:2, withWriteThrottling:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: WriteTagThrottling(2), HealthMetricsApi(2). Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for WriteTagThrottling(2), HealthMetricsApi(2). Clear-after-test modes: none. Timeouts: none.
