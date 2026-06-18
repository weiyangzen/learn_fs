<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml

## Purpose
Runs BulkDump/BulkLoad restore through MockS3 with very light injected S3 errors, throttling, and delays.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BackupS3BlobBulkLoadRestoreWithChaos. Workload entry points are `Cycle`, `BackupS3BlobCorrectness`. Configuration keys include testClass='Backup', configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=True, simpleConfig=False, minimumRegions=2, extraMachineCountDC=3, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False, faultInjection=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `Cycle`(nodeCount=200, transactionsPerSecond=150.0, testDuration=30.0); `BackupS3BlobCorrectness`(backupAfter=15.0, restoreStartAfterBackupFinished=60.0, abortAndRestartAfter=0.0, stopDifferentialAfter=0.0, performRestore=True, backupRangesCount=-1, skipDirtyRestore=False, backupURL='blobstore://mocks3:mocksecret:mocktoken@127.0.0.1:8080/backup_container?bucket=backup_bucket&region=us-east-1&secure_connection=0&cwpf=1&cu=1').

## State And Persistence Behavior
Persistent and simulated state touched: backup/restore state, backup tags, mutation logs, extra database state, or restore target contents, application key-space data used for correctness validation, mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BackupS3BlobBulkLoadRestoreWithChaos: useDB=True, clearAfterTest=False, simBackupAgents='BackupToFile', waitForQuiescence=False, waitForQuiescenceEnd=False, runConsistencyCheck=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=7200.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, bulkdump_job_timeout=5400, bulkload_job_timeout=5400; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=600, blobstore_request_timeout_min=600, blobstore_request_tries=20, blobstore_connect_tries=20, blobstore_connect_timeout=120, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: BackupToFile, blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.005, throttleRate=0.01, delayRate=0.005, corruptionRate=0.0, maxDelay=0.3; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs; some tests intentionally preserve state across blocks, so reordering or clearing data changes semantics.

## Test Signals
correctness workloads verify data, API, serializability, latency, or data-distribution invariants; restore and backup correctness workloads verify backup output against restored data
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BackupS3BlobBulkLoadRestoreWithChaos.toml -->
