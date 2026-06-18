# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestAttrition-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 14 lines, 262 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapTestVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapTestVerify) and schedules each block's workload list (SnapTestVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False, SnapTestVerify/SnapTest.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
