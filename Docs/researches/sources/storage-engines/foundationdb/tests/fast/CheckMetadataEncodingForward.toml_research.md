# Research: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml

- **Purpose:** Fast simulation test specification for the `CheckMetadataEncodingForward` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 17 lines, 347 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CheckMetadataEncodingForward, workloads Cycle, RandomMoveKeys, CheckMetadataEncoding, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CheckMetadataEncodingForward) and schedules each block's workload list (CheckMetadataEncodingForward:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, RandomMoveKeys, CheckMetadataEncoding. Top-level keys: knobs. Configuration/test knobs: CheckMetadataEncodingForward/Cycle.testDuration=10.0, CheckMetadataEncodingForward/Cycle.transactionsPerSecond=2500.0, CheckMetadataEncodingForward/RandomMoveKeys.testDuration=10.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, RandomMoveKeys, CheckMetadataEncoding. Clear-after-test modes: none. Timeouts: none.
