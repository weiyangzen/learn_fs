<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml -->
# sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml

## Purpose
Runs S3ClientWorkload across stable, light, medium, and heavy MockS3 chaos rates.

## Important APIs, Types, And Functions
This file is consumed by the FoundationDB simulation test harness as TOML. It declares 4 `[[test]]` block(s): S3ClientWorkloadStable, S3ClientWorkloadLightChaos, S3ClientWorkloadMediumChaos, S3ClientWorkloadHeavyChaos. Workload entry points are `S3ClientWorkload`, `S3ClientWorkload`, `S3ClientWorkload`, `S3ClientWorkload`. Configuration keys include no top-level configuration beyond tests.

## Control Flow
The simulation runner executes the test blocks in file order; later blocks often depend on persisted data, backup tags, or restored state from earlier blocks.
Workload detail: `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.0, throttleRate=0.0, delayRate=0.0, corruptionRate=0.0, maxDelay=0.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.05, throttleRate=0.02, delayRate=0.1, corruptionRate=0.01, maxDelay=1.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.15, throttleRate=0.08, delayRate=0.2, corruptionRate=0.03, maxDelay=2.0); `S3ClientWorkload`(enableChaos=True, s3Url='blobstore://testkey:testsecret:testtoken@127.0.0.1:8080/?bucket=s3clientworkload&region=us-east-1&secure_connection=0&bypass_simulation=0&global_connection_pool=0', errorRate=0.3, throttleRate=0.15, delayRate=0.4, corruptionRate=0.05, maxDelay=3.0).

## State And Persistence Behavior
Persistent and simulated state touched: mock S3/blobstore objects and bulk dump/load job metadata.
Clear/setup flags and state controls are declared on tests as: S3ClientWorkloadStable: default flags; S3ClientWorkloadLightChaos: default flags; S3ClientWorkloadMediumChaos: default flags; S3ClientWorkloadHeavyChaos: default flags.

## Dependencies And Integration Points
FoundationDB simulation TOML runner; workload implementations named by `testName`.

## Risks
chaos rates can compound across many S3/blobstore operations: errorRate=0.0, throttleRate=0.0, delayRate=0.0, corruptionRate=0.0, maxDelay=0.0; errorRate=0.05, throttleRate=0.02, delayRate=0.1, corruptionRate=0.01, maxDelay=1.0; errorRate=0.15, throttleRate=0.08, delayRate=0.2, corruptionRate=0.03, maxDelay=2.0; errorRate=0.3, throttleRate=0.15, delayRate=0.4, corruptionRate=0.05, maxDelay=3.0.

## Test Signals
The presence of the configured workload as a slow simulation test is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/S3ClientWorkloadWithChaos.toml -->
