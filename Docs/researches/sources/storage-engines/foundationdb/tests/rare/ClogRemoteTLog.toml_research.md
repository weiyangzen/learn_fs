# Research: sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml

- **Purpose:** Rare simulation test specification for the `ClogRemoteTLog` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 42 lines, 1126 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClogRemoteTLog, workloads Cycle, ClogRemoteTLog, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClogRemoteTLog) and schedules each block's workload list (ClogRemoteTLog:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, ClogRemoteTLog. Top-level keys: configuration, knobs. Configuration/test knobs: processesPerMachine=1, machineCount=30, generateFearless=True, minimumRegions=2, remoteDesiredTLogCount=4, statelessProcessClassesPerDC=2, ClogRemoteTLog/Cycle.testDuration=360.0, ClogRemoteTLog/Cycle.transactionsPerSecond=250.0, ClogRemoteTLog/Cycle.nodeCount=30, ClogRemoteTLog/ClogRemoteTLog.testDuration=360.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, ClogRemoteTLog. Clear-after-test modes: none. Timeouts: none.
