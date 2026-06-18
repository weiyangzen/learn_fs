# sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.cpp

Purpose: Provides database cleanup, HTML dumping, metric aggregation/logging, and post-test consistency-scan control for tester runs.

Important APIs/types/functions: `clearData` clears `normalKeys` and verifies emptiness. `toHTML` escapes binary keys/values for dumps. `dumpDatabase` scans a key range into an HTML file at a consistent read version. `aggregateMetrics` groups `PerfMetric`s by name and sums or averages them. `logMetrics` writes metrics as trace events. `checkConsistencyScanAfterTest` enables/disables simulated consistency scans based on `TesterConsistencyScanState`.

Control flow: `clearData` uses one transaction to clear and commit, then a second RAW_ACCESS transaction to verify no normal keys remain, retrying both loops through `onError`. `dumpDatabase` opens output, gets a read version, paginates `getRange` in batches of 1000, writes escaped rows, and retries on transaction errors. Metric aggregation is synchronous. Consistency-scan handling disables repeat execution by clearing `enabled`, optionally enables the scan, then disables it with optional wait-for-complete.

State and persistence behavior: `clearData` durably removes user data under `normalKeys`. `dumpDatabase` writes a local HTML file. Consistency-scan helpers mutate simulation/management state. Metrics are not persisted except trace output.

Dependencies and integration points: Uses native transactions, system key constants, management APIs, `PerfMetric`, `TraceEvent`, `fdbrpc/sim_validation.h`, and `QuietDatabase` support. Called by `runTest` in `test.cpp`.

Risks: `clearData` asserts if any key remains, so bugs or tenant/system-key misunderstandings become hard failures. `dumpDatabase` writes a file named from test title and can expose raw test data in HTML. `aggregateMetrics` assumes same-named metrics have compatible averaging/format metadata.

Test signals: Trace events include clear phases, database dumped filename, metric traces, and consistency-scan progress. `TesterClearFailure` is the critical failure signal for cleanup.
