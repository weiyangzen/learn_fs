# Research: sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml

- **Purpose:** Rare simulation test specification for the `ReadSkewReadWrite` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 24 lines, 558 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SkewedReadWriteTest, workloads SkewedReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SkewedReadWriteTest) and schedules each block's workload list (SkewedReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SkewedReadWrite. Top-level keys: none. Configuration/test knobs: SkewedReadWriteTest.runSetup=True, SkewedReadWriteTest/SkewedReadWrite.testDuration=40.0, SkewedReadWriteTest/SkewedReadWrite.transactionsPerSecond=100, SkewedReadWriteTest/SkewedReadWrite.nodeCount=3000.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SkewedReadWrite. Clear-after-test modes: SkewedReadWriteTest:True. Timeouts: SkewedReadWriteTest:3600.0.
