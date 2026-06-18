# sources/storage-engines/tikv/tests/integrations/resource_metering/test_cpu.rs

Purpose: verifies resource metering records non-zero CPU time for tagged storage and coprocessor workloads.

Important APIs and functions: `test_prewrite`, `test_commit`, `test_reschedule_coprocessor`, `test_get`, `test_batch_get`, `test_batch_get_command`; `setup_test_suite` builds `TestSuite`, `Store`, read pool, `Endpoint`, `ConcurrencyManager`, and `QuotaLimiter`; `prepare_insert` creates table mutations; `require_cpu_time_not_zero` subscribes to records and filters by tag; `cpu_load` burns CPU under failpoints.

Control flow: each test installs a failpoint that injects CPU work into a selected execution path, starts a pubsub observer for a resource-group tag, runs a tagged workload, and asserts summed `cpu_time_ms` is positive. Coprocessor coverage inserts rows, commits, builds a DAG request with resource tag/source, forces rescheduling, and checks a non-empty response.

State and persistence: uses temporary Rocks-backed storage through `TestSuite`; resource metering state is in recorder/reporter workers and pubsub streams. Transaction tests persist MVCC data before reads or commits.

Dependencies and integration: storage scheduler, point getter, batch-get command, coprocessor endpoint, failpoints, thread-group properties, resource control, and shared resource metering test harness.

Risks: failpoint names and CPU timing are brittle; record delivery depends on thread registration, report interval, and CI scheduling.

Test signals: confirms tag propagation and CPU accounting for prewrite, commit, point get, batch get, batch-get command, and coprocessor execution.
