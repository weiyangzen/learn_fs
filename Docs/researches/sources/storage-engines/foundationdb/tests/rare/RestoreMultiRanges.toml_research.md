# Research: sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml

- **Purpose:** Rare simulation test specification for the `RestoreMultiRanges` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 14 lines, 303 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RestoreMultiRanges, workloads RestoreMultiRanges, top-level keys configuration, testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RestoreMultiRanges) and schedules each block's workload list (RestoreMultiRanges:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RestoreMultiRanges. Top-level keys: configuration, testPriority. Configuration/test knobs: RestoreMultiRanges.simBackupAgents='BackupToFile'.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RestoreMultiRanges. Clear-after-test modes: RestoreMultiRanges:True. Timeouts: none.
