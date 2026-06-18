# sources/storage-engines/foundationdb/fdbserver/workloads/BulkDumping.cpp

## Purpose
`BulkDumping.cpp` defines `BulkDumpingWorkload`, an end-to-end simulation test for exporting data with bulk dump and importing it with bulk load. It creates known random data, dumps a selected range to a filesystem or blobstore root, clears database and bulk metadata, reloads a selected range from the dump output, checks loaded data against the original dataset, and validates bulk load job history.

## Important APIs, Types, And Functions
The workload uses `BulkDumpState`, `BulkLoadJobState`, `BulkLoadTaskState`, `BulkLoadTransportMethod`, `createBulkDumpJob`, `submitBulkDumpJob`, `getSubmittedBulkDumpJob`, `setBulkDumpMode`, `createBulkLoadJob`, `submitBulkLoadJob`, `getRunningBulkLoadJob`, `cancelBulkLoadJob`, `acknowledgeAllErrorBulkLoadTasks`, and range-lock helpers such as `registerRangeLockOwner`. Mock S3 integration comes from `MockS3Server`, `MockS3ServerChaos`, and `S3FaultInjector`.

## Control Flow
`setup` optionally registers/configures a mock S3 server on client 0 for blobstore tests. `start` runs only on client 0, clears mock storage for blobstore simulation, disables connection failures, selects a dump range, writes 1000 ordered KVs, registers the bulk-load range-lock owner, enables bulk dump mode, submits a dump job, waits for no submitted dump job, clears data and bulk metadata, enables bulk load mode, submits a load job over either the dump range or a random range, waits for completion/error/cancellation, compares loaded KVs when range coverage is valid, acknowledges error tasks, validates job history, and removes the range-lock owner.

## State And Persistence
The workload writes normal keyspace data, system-key bulk dump and load metadata, range-lock owner state, job history, and filesystem/blobstore objects under `simfdb/bulkdump` or `jobRoot`. `clearDatabase` intentionally clears `normalKeys`, `bulkDumpKeys`, `bulkLoadJobKeys`, `bulkLoadTaskKeys`, and `bulkLoadJobHistoryKeys` before reloading.

## Dependencies And Integration Points
This test exercises the public bulk dump/load client APIs, DD mode toggles, KRM-backed task state, bulk-load range locking, the simulator, and optional mock S3 handlers. It disables workloads that race on DD mode, storage movement/corruption, validation, and random range locking.

## Risks
The job wait loops include timeout fallbacks that can proceed with intermediate task states, so a timeout-heavy run can validate partial state rather than full completion. Cancellation is currently disabled by forcing `maxCancelTimes = 0` because job IDs are random. Range coverage matters: if the load range is not contained by the dump range, data comparison is skipped and the expected result shifts to job-history error validation. Mock S3 handler reuse and chaos options can leak cross-test state if cleanup is incomplete.

## Test Signals
Important traces include `BulkDumpingWorkLoadSetKey`, `BulkDumpingWorkLoadDumpJobTimeout`, `BulkDumpingWorkLoadJobTimeout`, `BulkDumpingWorkLoadBulkLoadTaskWrongPhase`, `BulkDumpingWorkLoadError`, `BulkDumpingWorkLoadSetDumpModeFailed`, `BulkDumpingWorkLoadSetLoadModeFailed`, and mock S3 registration/chaos traces. The explicit `ASSERT`s around range locks, job history, and data equality are the primary pass/fail signals.
