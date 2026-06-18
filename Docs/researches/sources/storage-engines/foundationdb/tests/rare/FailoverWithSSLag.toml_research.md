# Research: sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml

- **Purpose:** Rare simulation test specification for the `FailoverWithSSLag` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 18 lines, 361 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles FailoverWithSSLag, workloads Cycle, FailoverWithSSLagWorkload, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (FailoverWithSSLag) and schedules each block's workload list (FailoverWithSSLag:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, FailoverWithSSLagWorkload. Top-level keys: configuration. Configuration/test knobs: generateFearless=True, processesPerMachine=1, machineCount=20, minimumRegions=2, FailoverWithSSLag/Cycle.testDuration=200.0, FailoverWithSSLag/Cycle.transactionsPerSecond=250.0, FailoverWithSSLag/Cycle.nodeCount=3000, FailoverWithSSLag/FailoverWithSSLagWorkload.testDuration=1000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, FailoverWithSSLagWorkload. Clear-after-test modes: none. Timeouts: none.
