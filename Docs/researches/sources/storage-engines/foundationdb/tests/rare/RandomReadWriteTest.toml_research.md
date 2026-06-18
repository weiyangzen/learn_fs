# Research: sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml

- **Purpose:** Rare simulation test specification for the `RandomReadWriteTest` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 7 lines, 152 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RandomReadWriteTest, workloads ReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RandomReadWriteTest) and schedules each block's workload list (RandomReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ReadWrite. Top-level keys: none. Configuration/test knobs: RandomReadWriteTest/ReadWrite.testDuration=30.0, RandomReadWriteTest/ReadWrite.transactionsPerSecond=1000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ReadWrite. Clear-after-test modes: none. Timeouts: none.
