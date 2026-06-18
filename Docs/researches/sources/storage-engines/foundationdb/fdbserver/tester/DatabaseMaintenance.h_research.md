# sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.h

Purpose: Declares tester maintenance helpers and the consistency-scan state struct shared with the main orchestrator.

Important APIs/types/functions: `TesterConsistencyScanState` contains `enabled`, `enableAfter`, and `waitForComplete`. Declares `clearData`, `dumpDatabase`, `aggregateMetrics`, and `checkConsistencyScanAfterTest`.

Control flow: No implementation flow in the header; the struct flags drive the conditional flow in `DatabaseMaintenance.cpp` and `test.cpp`.

State and persistence behavior: The struct is transient in-memory state carried across a test run. The declared functions can mutate database contents, write dump files, and alter simulated scan state.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h` for `Database`, `Future`, `KeyRange`, and `PerfMetric`. Used by `test.cpp` and the tester library.

Risks: `TesterConsistencyScanState*` is passed raw to async functions; callers must ensure lifetime across suspension points. Defaults keep scans disabled unless the orchestrator enables them.

Test signals: Compile/link coverage plus runtime traces from the implementation.
