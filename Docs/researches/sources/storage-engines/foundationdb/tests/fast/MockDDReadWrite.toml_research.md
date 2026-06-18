# Research: sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml

- **Purpose:** Fast simulation test specification for the `MockDDReadWrite` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 27 lines, 495 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles MockDDTracker, MockDDReadWriteTest, workloads MockDDTrackerShardEvaluator, MockDDReadWrite, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (MockDDTracker, MockDDReadWriteTest) and schedules each block's workload list (MockDDTracker:1, MockDDReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MockDDTrackerShardEvaluator, MockDDReadWrite. Top-level keys: configuration, knobs. Configuration/test knobs: testClass='MockDD', MockDDTracker/MockDDTrackerShardEvaluator.testDuration=50.0, MockDDReadWriteTest/MockDDReadWrite.testDuration=500.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MockDDTrackerShardEvaluator, MockDDReadWrite. Clear-after-test modes: none. Timeouts: none.
