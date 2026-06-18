<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml

## Purpose
Runs stable, light, medium, and heavy S3 chaos variants of BulkDumpingWorkload with long-running timeouts.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): BulkDumpingS3Stable, BulkDumpingS3LightChaos, BulkDumpingS3MediumChaos, BulkDumpingS3HeavyChaos. Workload entry points are `BulkDumpingWorkload`, `BulkDumpingWorkload`, `BulkDumpingWorkload`, `BulkDumpingWorkload`. Configuration keys include configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, longRunningTest=True, generateFearless=False, simpleConfig=False, minimumRegions=1, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.03, throttleRate=0.02, delayRate=0.08, corruptionRate=0.01); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.08, throttleRate=0.05, delayRate=0.15, corruptionRate=0.02); `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0, enableChaos=True, errorRate=0.15, throttleRate=0.1, delayRate=0.25, corruptionRate=0.03).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BulkDumpingS3Stable: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=3600; BulkDumpingS3LightChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=7200, maxDDRunTime=2400; BulkDumpingS3MediumChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=10800, maxDDRunTime=3600; BulkDumpingS3HeavyChaos: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=14400, maxDDRunTime=5400.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0; client knobs: blobstore_max_delay_retryable_error=2, blobstore_max_delay_connection_failed=1; backup agents/modes: blobstore.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.03, throttleRate=0.02, delayRate=0.08, corruptionRate=0.01, maxDelay=0.5; errorRate=0.08, throttleRate=0.05, delayRate=0.15, corruptionRate=0.02, maxDelay=1.0; errorRate=0.15, throttleRate=0.1, delayRate=0.25, corruptionRate=0.03, maxDelay=2.0; bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3WithChaos.toml -->
