## sources/storage-engines/tikv/components/resource_metering/tests/summary_test.rs

Purpose: integration test for summary counter flow from thread-local recording through recorder, reporter, and a registered `DataSink`.

Important APIs/types/functions: `MockDataSink`, `test_summary`, constants `PRECISION_MS` and `REPORT_INTERVAL_MS`. The sink stores latest records by resource group tag.

Control flow: the test starts recorder and reporter, verifies counters are not emitted before a sink registers, registers the sink, records read/write keys under a tag and verifies sums after report interval, drops the guard, then verifies counters stop flowing.

State/persistence: in-memory `HashMap<Vec<u8>, ResourceUsageRecord>` protected by `Mutex`; worker state is stopped at the end.

Dependencies/integration: uses public `init_recorder`, `init_reporter`, `record_read_keys`, `record_write_keys`, kvproto context tags, and `ReadableDuration` config.

Risks: sleeps depend on configured precision/report intervals and can be slow/flaky under severe scheduling delay. It validates read/write keys but not network/logical byte gates.

Test signals: verifies the activation contract: reporter data-sink registration causes recorder collection to start, and dropping the sink stops reporting.
