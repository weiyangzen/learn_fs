# Research: sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml

- **Purpose:** Fast simulation test specification for the `PerpetualWiggleStats` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 117 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles PerpetualWiggleStats, workloads PerpetualWiggleStatsWorkload, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (PerpetualWiggleStats) and schedules each block's workload list (PerpetualWiggleStats:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: PerpetualWiggleStatsWorkload. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for PerpetualWiggleStatsWorkload. Clear-after-test modes: none. Timeouts: none.
