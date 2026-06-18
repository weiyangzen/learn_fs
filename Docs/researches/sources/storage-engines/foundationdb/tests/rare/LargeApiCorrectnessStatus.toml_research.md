# Research: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml

- **Purpose:** Rare simulation test specification for the `LargeApiCorrectnessStatus` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 30 lines, 681 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads ApiCorrectness, Status, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, Status. Top-level keys: none. Configuration/test knobs: ApiCorrectnessTest.runSetup=True, ApiCorrectnessTest/Status.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, Status. Clear-after-test modes: ApiCorrectnessTest:True. Timeouts: ApiCorrectnessTest:2100.
