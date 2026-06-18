<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3Client.toml -->
# sources/storage-engines/foundationdb/tests/slow/S3Client.toml

## Purpose
Validates S3ClientWorkload upload/download/delete against MockS3 with fault injection disabled and verbose blobstore logging.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 1 `[[test]]` block(s): S3Client. Workload entry points are `S3ClientWorkload`. Configuration keys include buggify=False.

## Control Flow
The simulation runner creates the configured cluster, applies global knobs/configuration, and runs the listed workloads concurrently within the single test block.
Workload detail: `S3ClientWorkload`(s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0').

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: S3Client: runFailureWorkloads=False.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`; simulation knobs: ; Flow/network/blobstore knobs: MAX_BUGGIFIED_DELAY=0.0, http_verbose_level=10, s3client_verbose_level=10, blobstore_verbose_level=10, blobstore_max_connection_life=300, blobstore_request_timeout_min=300, blobstore_request_tries=5, blobstore_connect_tries=5, blobstore_connect_timeout=30, http_send_size=1024, http_read_size=1024, connection_monitor_loop_time=0.1, connection_monitor_timeout=1.0, connection_monitor_idle_timeout=60.0.

## Risks
risk is mainly coverage drift if the named workload implementation changes while this config remains unchanged.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3Client.toml -->
