<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml -->
# sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml

## Purpose
Runs BulkDumpingWorkload using blobstore transport to a mock S3 URL under deterministic bulk-load knobs.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): BulkDumpingWorkloadS3. Workload entry points are `BulkDumpingWorkload`. Configuration keys include configuration=storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True, generateFearless=False, simpleConfig=False, minimumRegions=1, config='triple usable_regions=1 storage_engine=ssd-2 perpetual_storage_wiggle=0 commit_proxies=3 grv_proxies=3 resolvers=3 logs=3', buggify=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `BulkDumpingWorkload`(bulkLoadTransportMethod=2, jobRoot='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=bulkdumping&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0&connect_timeout=60&request_timeout=120', maxCancelTimes=0).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: BulkDumpingWorkloadS3: useDB=True, waitForQuiescence=False, connectionFailuresDisableDuration=1000000, runFailureWorkloads=False, timeout=3600.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: bulkload_sim_failure_injection=False, shard_encode_location_metadata=True, enable_read_lock_on_range=True, enable_version_vector=False, enable_version_vector_tlog_unicast=False, enable_version_vector_reply_recovery=False, min_byte_sampling_probability=0.5, cc_enforce_use_unfit_dd_in_sim=True, disable_audit_storage_final_replica_check_in_sim=True, max_trace_lines=5000000; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0, dd_team_zero_server_left_log_delay=0, dd_rebalance_parallelism=1; backup agents/modes: blobstore.

## Risks
bulk dump/load and blobstore behavior depends on storage-engine exclusions, mock S3 URL parameters, and long job timeout knobs.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/BulkDumpingS3.toml -->
