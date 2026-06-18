# Research: sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml

- **Purpose:** Fast simulation test specification for the `GetEstimatedRangeSize` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 13 lines, 276 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles GetEstimatedRangeSizeTest, workloads GetEstimatedRangeSize(2), top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (GetEstimatedRangeSizeTest) and schedules each block's workload list (GetEstimatedRangeSizeTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: GetEstimatedRangeSize(2). Top-level keys: configuration. Configuration/test knobs: GetEstimatedRangeSizeTest/GetEstimatedRangeSize.nodeCount=250000, GetEstimatedRangeSizeTest/GetEstimatedRangeSize.nodeCount=250000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for GetEstimatedRangeSize(2). Clear-after-test modes: none. Timeouts: none.
